import os
import json
import time
import random
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import ValidationError

from agent.models import AppInput, AppResearchResult
from agent.tools import search_web, fetch_page, check_mcp_support, verify_url, get_composio_client

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(api_key=GEMINI_API_KEY)

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "research_results.json")

SYSTEM_PROMPT = """You are a senior AI Product Ops specialist evaluating SaaS applications for Composio's agent toolkit catalog.
Composio turns software apps into toolkits and MCP servers that AI agents can call.

For the given application, evaluate its integration feasibility based on real-world developer facts and documentation:
1. Category & 1-line description of what it does.
2. Auth method(s): OAuth2, API Key, Basic Auth, Token, CLI/None, etc.
3. Self-serve vs Gated:
   - "Self-serve": A developer can register freely or start an un-gated self-serve trial.
   - "Partially Gated": Requires developer application review, paid plan, or merchant onboarding (e.g., Amazon SP-API, WhatsApp Business, Google Ads dev token).
   - "Enterprise/Sales Gated": Requires speaking to sales, contract, or partner agreement (e.g., DealCloud, PitchBook, iPayX).
   - "Open Source / Local": Runs locally or self-hosted, no commercial gate (e.g., Sherlock, Mermaid CLI, Twenty self-hosted).
4. API Surface: REST, GraphQL, REST & GraphQL, CLI / Local Executable, or Private/Closed.
5. API Breadth: "Broad (>50 endpoints)", "Medium (10-50 endpoints)", "Narrow (<10 endpoints)", or "CLI / Local Tool".
6. Existing MCP: Does an official or community MCP server exist?
7. Buildability Verdict:
   - "Easy (Ready today)": Self-serve + clear API key/OAuth + well-documented REST/GraphQL or open-source CLI.
   - "Medium (App approval / OAuth required)": Requires OAuth app verification, specific scopes, or developer portal registration.
   - "Hard (Enterprise / Sales gated)": Gated behind enterprise sales, expensive subscription, or partner approval.
   - "Blocked (No public API)": Closed platform, private consumer UI only, or discontinued API.
8. Blocker Analysis: What is the primary technical, commercial, or operational blocker if Composio builds a toolkit?
9. Evidence URLs: Real, authoritative documentation URLs.

Respond ONLY with a valid JSON object matching the requested schema. No markdown formatting, no code fencing."""

RESEARCH_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "description": {"type": "STRING"},
        "auth_methods": {"type": "ARRAY", "items": {"type": "STRING"}},
        "auth_notes": {"type": "STRING"},
        "self_serve": {"type": "STRING"},
        "self_serve_detail": {"type": "STRING"},
        "api_surface": {"type": "STRING"},
        "api_breadth": {"type": "STRING"},
        "existing_mcp": {"type": "BOOLEAN"},
        "mcp_details": {"type": "STRING"},
        "buildability": {"type": "STRING"},
        "blocker_analysis": {"type": "STRING"},
        "evidence_urls": {"type": "ARRAY", "items": {"type": "STRING"}},
        "confidence_score": {"type": "NUMBER"}
    },
    "required": [
        "description", "auth_methods", "auth_notes", "self_serve",
        "self_serve_detail", "api_surface", "api_breadth", "existing_mcp",
        "mcp_details", "buildability", "blocker_analysis", "evidence_urls"
    ]
}


def load_cached_results() -> Dict[int, AppResearchResult]:
    """Loads existing results from disk for atomic checkpointing."""
    if not os.path.exists(RESULTS_FILE):
        return {}
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["id"]: AppResearchResult(**item) for item in data}
    except Exception as e:
        print(f"Warning loading cache: {e}")
        return {}


def save_result_atomic(result: AppResearchResult):
    """Atomically updates the results JSON file."""
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    current_results = load_cached_results()
    if result.id in current_results:
        existing = current_results[result.id]
        if result.human_report_status is None and existing.human_report_status is not None:
            result.human_report_status = existing.human_report_status
        if result.human_report is None and existing.human_report is not None:
            result.human_report = existing.human_report
        if result.mcp_url is None and existing.mcp_url is not None:
            result.mcp_url = existing.mcp_url
        if result.verification_notes is None and existing.verification_notes is not None:
            result.verification_notes = existing.verification_notes
    current_results[result.id] = result

    sorted_data = [current_results[k].model_dump() for k in sorted(current_results.keys())]

    tmp_file = f"{RESULTS_FILE}.tmp"
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(sorted_data, f, indent=2)
    os.replace(tmp_file, RESULTS_FILE)


def research_app(app: AppInput, max_retries: int = 3, save: bool = True) -> AppResearchResult:
    """Researches a single app using Composio-backed search/fetch (with httpx fallback) + Gemini extraction."""
    print(f"\n[Agent] Researching #{app.id}: {app.name} ({app.category})...")

    composio_client = get_composio_client()
    if composio_client:
        print(f"[Composio SDK] Executing search & fetch tools via Composio for #{app.id} {app.name}")
    else:
        print(f"[Scraper] COMPOSIO_API_KEY not set; using direct httpx fallback for #{app.id} {app.name}")

    # Step 1: Web search (routes through Composio SDK when configured)
    query1 = f"{app.name} API developer documentation authentication {app.hint}"
    query2 = f"{app.name} API key OAuth self-serve pricing developer account"

    search_results = search_web(query1, max_results=3, app_name=app.name, hint=app.hint)
    search_results += search_web(query2, max_results=2, app_name=app.name, hint=app.hint)

    # Step 2: Check MCP registry
    mcp_info = check_mcp_support(app.name)

    # Step 3: Fetch top docs snippet if URL found (routes through Composio SDK when configured)
    doc_text = ""
    top_urls = [r["url"] for r in search_results if r["url"].startswith("http")]
    if top_urls:
        doc_text = fetch_page(top_urls[0], max_chars=1800)

    search_context = "\n".join(
        [f"- Title: {r['title']}\n  URL: {r['url']}\n  Snippet: {r['snippet']}" for r in search_results]
    )

    user_prompt = f"""Target Application:
Name: {app.name}
Category: {app.category}
Hint / Website: {app.hint}

Known MCP Status:
Exists: {mcp_info['exists']}
Details: {mcp_info['details']}

Live Web Search Context:
{search_context}

Documentation Text Snippet:
{doc_text[:1200] if doc_text else 'N/A'}

Analyze this application thoroughly and return the structured JSON assessment according to the Product Ops rubric."""

    # Step 4: LLM Generation with Exponential Backoff
    for attempt in range(max_retries):
        try:
            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=RESEARCH_SCHEMA,
                temperature=0.1
            )

            resp = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=user_prompt,
                config=config
            )

            raw_json = json.loads(resp.text)

            if mcp_info["exists"] and not raw_json.get("existing_mcp"):
                raw_json["existing_mcp"] = True
                raw_json["mcp_details"] = mcp_info["details"]

            evidence = raw_json.get("evidence_urls", [])
            for u in top_urls[:2]:
                if u not in evidence:
                    evidence.append(u)
            raw_json["evidence_urls"] = evidence[:3]

            result = AppResearchResult(
                id=app.id,
                name=app.name,
                category=app.category,
                hint=app.hint,
                description=raw_json["description"],
                auth_methods=raw_json["auth_methods"],
                auth_notes=raw_json["auth_notes"],
                self_serve=raw_json["self_serve"],
                self_serve_detail=raw_json["self_serve_detail"],
                api_surface=raw_json["api_surface"],
                api_breadth=raw_json["api_breadth"],
                existing_mcp=raw_json["existing_mcp"],
                mcp_details=raw_json["mcp_details"],
                mcp_url=mcp_info.get("url"),
                buildability=raw_json["buildability"],
                blocker_analysis=raw_json["blocker_analysis"],
                evidence_urls=raw_json["evidence_urls"],
                confidence_score=raw_json.get("confidence_score", 0.92),
                verification_status="Pass 1 Complete"
            )

            existing_cached = load_cached_results().get(app.id)
            if existing_cached:
                if result.human_report is None and existing_cached.human_report is not None:
                    result.human_report = existing_cached.human_report
                if result.human_report_status is None and existing_cached.human_report_status is not None:
                    result.human_report_status = existing_cached.human_report_status
                if result.mcp_url is None and existing_cached.mcp_url is not None:
                    result.mcp_url = existing_cached.mcp_url
                if result.verification_notes is None and existing_cached.verification_notes is not None:
                    result.verification_notes = existing_cached.verification_notes

            if save:
                save_result_atomic(result)
            print(f"[Agent] ✓ Successfully researched #{app.id} {app.name}: Verdict = {result.buildability}, Auth = {result.auth_methods}")
            return result

        except Exception as e:
            wait_time = (attempt + 1) * 3 + random.uniform(0.5, 1.5)
            print(f"[Agent] Error researching #{app.id} {app.name} (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"[Agent] Backing off for {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                fallback = AppResearchResult(
                    id=app.id,
                    name=app.name,
                    category=app.category,
                    hint=app.hint,
                    description=f"{app.name} platform in {app.category}",
                    auth_methods=["API Key"],
                    auth_notes="Requires developer documentation verification",
                    self_serve="Partially Gated",
                    self_serve_detail="Check developer portal for credentials",
                    api_surface="REST",
                    api_breadth="Medium (10-50 endpoints)",
                    existing_mcp=mcp_info["exists"],
                    mcp_details=mcp_info["details"],
                    mcp_url=mcp_info.get("url"),
                    buildability="Medium (App approval / OAuth required)",
                    blocker_analysis="Requires developer verification and documentation review",
                    evidence_urls=[f"https://{app.hint}" if not app.hint.startswith("http") else app.hint],
                    confidence_score=0.6,
                    verification_status="Flagged for Verification"
                )
                existing_cached = load_cached_results().get(app.id)
                if existing_cached:
                    if fallback.human_report is None and existing_cached.human_report is not None:
                        fallback.human_report = existing_cached.human_report
                    if fallback.human_report_status is None and existing_cached.human_report_status is not None:
                        fallback.human_report_status = existing_cached.human_report_status
                    if fallback.mcp_url is None and existing_cached.mcp_url is not None:
                        fallback.mcp_url = existing_cached.mcp_url
                    if fallback.verification_notes is None and existing_cached.verification_notes is not None:
                        fallback.verification_notes = existing_cached.verification_notes

                if save:
                    save_result_atomic(fallback)
                return fallback


def run_research_batch(apps: List[AppInput], resume: bool = True) -> List[AppResearchResult]:
    """Runs research across the list of apps with checkpointing and polite rate-limiting."""
    cached = load_cached_results() if resume else {}
    results = []

    print(f"Starting research batch. Total apps: {len(apps)}. Already cached: {len(cached)}")

    for app in apps:
        if resume and app.id in cached:
            print(f"[Agent] Skipping #{app.id} {app.name} (already cached)")
            results.append(cached[app.id])
            continue

        res = research_app(app)
        results.append(res)
        time.sleep(1.2)

    return results
