"""
verify_composio.py -- Standalone Verification Script for Composio Tools & Pipeline

Verifies:
1. Composio Client instantiation (get_composio_client)
2. Live Web Search routing via Composio (search_web)
3. Live Web Fetch routing via Composio (fetch_page)
4. Telemetry Tracking & Metrics Reporting (get_tool_telemetry)
5. Single-app research execution with Gemini (research_app)
6. Pattern Analyzer & statistical metrics (analyze_patterns)
"""

import os
import sys
import time
import json
import tempfile
from dotenv import load_dotenv

load_dotenv()


def test_environment_keys():
    print("\n--- [Step 1] Environment & Keys Verification ---")
    composio_key = os.getenv("COMPOSIO_API_KEY", "")
    composio_user = os.getenv("COMPOSIO_USER_ID", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    assert composio_key, "COMPOSIO_API_KEY is missing from environment!"
    assert composio_user, "COMPOSIO_USER_ID is missing from environment!"
    assert gemini_key, "GEMINI_API_KEY is missing from environment!"

    # Safely display masked values (never print full secret)
    masked_composio = f"{composio_key[:4]}...{composio_key[-4:]} (len={len(composio_key)})"
    masked_gemini = f"{gemini_key[:4]}...{gemini_key[-4:]} (len={len(gemini_key)})"

    print(f"  [PASS] COMPOSIO_API_KEY present: {masked_composio}")
    print(f"  [PASS] COMPOSIO_USER_ID present: {composio_user}")
    print(f"  [PASS] GEMINI_API_KEY present:   {masked_gemini}")
    print(f"  [PASS] GEMINI_MODEL:            {gemini_model}")
    return True


def test_composio_client():
    print("\n--- [Step 2] Testing get_composio_client() ---")
    from agent.tools import get_composio_client

    client = get_composio_client()
    assert client is not None, "get_composio_client() returned None!"
    client_cls = type(client).__name__
    print(f"  [PASS] Composio client successfully instantiated: <{client_cls}>")
    return True


def test_search_web():
    print("\n--- [Step 3] Testing search_web() for Stripe ---")
    from agent.tools import search_web, get_tool_telemetry

    telemetry_before = get_tool_telemetry()
    composio_search_before = telemetry_before.get("composio_search", 0)

    start = time.time()
    results = search_web(
        query="Stripe API authentication",
        max_results=3,
        app_name="Stripe",
        hint="stripe.com"
    )
    elapsed = time.time() - start

    assert isinstance(results, list), f"Expected list, got {type(results)}"
    assert len(results) > 0, "search_web returned empty list!"
    for idx, r in enumerate(results, 1):
        assert "title" in r and "url" in r and "snippet" in r, f"Missing required keys in result {idx}"
        print(f"    [{idx}] {r['title'][:60]} -> {r['url']}")
    assert results[0]["url"].startswith("http"), "First result URL is invalid!"

    # Verify genuine Composio execution via telemetry
    telemetry_after = get_tool_telemetry()
    composio_search_after = telemetry_after.get("composio_search", 0)
    assert composio_search_after > composio_search_before, (
        f"Expected Composio to handle search_web, but composio_search count did not increase!"
    )

    print(f"  [PASS] Returned {len(results)} results via Composio in {elapsed:.2f}s")
    return True


def test_fetch_page():
    print("\n--- [Step 4] Testing fetch_page() for Stripe API docs ---")
    from agent.tools import fetch_page, get_tool_telemetry

    telemetry_before = get_tool_telemetry()
    composio_fetch_before = telemetry_before.get("composio_fetch", 0)

    start = time.time()
    url = "https://docs.stripe.com/api"
    content = fetch_page(url, max_chars=500)
    elapsed = time.time() - start

    assert isinstance(content, str), f"Expected str, got {type(content)}"
    assert len(content) > 50, f"fetch_page returned insufficient content: length={len(content)}"
    assert len(content) <= 500, f"fetch_page exceeded max_chars: length={len(content)}"
    assert "<script" not in content.lower(), "Fetched content contains unstripped <script> tags!"
    assert "<style" not in content.lower(), "Fetched content contains unstripped <style> tags!"

    # Verify genuine Composio execution via telemetry
    telemetry_after = get_tool_telemetry()
    composio_fetch_after = telemetry_after.get("composio_fetch", 0)
    assert composio_fetch_after > composio_fetch_before, (
        f"Expected Composio to handle fetch_page, but composio_fetch count did not increase!"
    )

    print(f"  [PASS] Fetched {len(content)} characters via Composio in {elapsed:.2f}s:")
    print(f"    Preview: \"{content[:140]}...\"")
    return True


def test_telemetry_reporting():
    print("\n--- [Step 5] Testing Telemetry Tracking & Metrics Reporting ---")
    from agent.tools import get_tool_telemetry, save_telemetry_metrics

    telemetry = get_tool_telemetry()
    assert isinstance(telemetry, dict), f"Expected dict, got {type(telemetry)}"
    assert "total_queries" in telemetry, "Missing total_queries in telemetry"
    assert "composio_queries" in telemetry, "Missing composio_queries in telemetry"
    assert "fallback_queries" in telemetry, "Missing fallback_queries in telemetry"
    assert "composio_share_pct" in telemetry, "Missing composio_share_pct in telemetry"
    assert "by_tool" in telemetry, "Missing by_tool in telemetry"
    assert "providers" in telemetry, "Missing providers in telemetry"
    assert "queries" in telemetry, "Missing queries list in telemetry"

    assert telemetry["total_queries"] >= 2, f"Expected total_queries >= 2, got {telemetry['total_queries']}"
    assert telemetry["composio_queries"] >= 2, f"Expected composio_queries >= 2, got {telemetry['composio_queries']}"
    assert telemetry["composio_search"] >= 1, "Composio search count should be >= 1"
    assert telemetry["composio_fetch"] >= 1, "Composio fetch count should be >= 1"

    print("  [PASS] Telemetry summary verified:")
    print(f"    - Total Queries:        {telemetry['total_queries']}")
    print(f"    - Composio Queries:     {telemetry['composio_queries']}")
    print(f"    - Fallback Queries:     {telemetry['fallback_queries']}")
    print(f"    - Composio Share:       {telemetry['composio_share_pct']}%")
    print(f"    - Search (Composio):    {telemetry['composio_search']}")
    print(f"    - Fetch (Composio):     {telemetry['composio_fetch']}")
    print(f"    - Providers Breakdown:  {telemetry['providers']}")

    # Test saving metrics to JSON
    temp_dir = tempfile.gettempdir()
    test_metrics_path = os.path.join(temp_dir, "test_telemetry_metrics.json")
    save_telemetry_metrics(test_metrics_path)
    assert os.path.exists(test_metrics_path), "Failed to save telemetry metrics file"
    with open(test_metrics_path, "r", encoding="utf-8") as f:
        saved_data = json.load(f)
    assert saved_data["total_queries"] == telemetry["total_queries"]
    try:
        os.remove(test_metrics_path)
    except Exception:
        pass
    print("  [PASS] save_telemetry_metrics() persistence verified.")

    return True


def test_single_app_research():
    print("\n--- [Step 6] Testing single-app research_app() with Gemini ---")
    from agent.models import AppInput, AppResearchResult
    from agent.researcher import research_app

    test_app = AppInput(
        id=1,
        name="Salesforce",
        category="CRM and Sales",
        hint="developer.salesforce.com"
    )

    start = time.time()
    print(f"  Dispatching research for #{test_app.id} {test_app.name}...")
    result = research_app(test_app, save=False)
    elapsed = time.time() - start

    assert isinstance(result, AppResearchResult), f"Expected AppResearchResult, got {type(result)}"
    assert result.id == 1, f"Expected app id 1, got {result.id}"
    assert result.name == "Salesforce", f"Expected Salesforce, got {result.name}"
    assert result.description, "Description should not be empty"
    assert len(result.auth_methods) > 0, "auth_methods should not be empty"
    assert result.self_serve in [
        "Self-serve", "Partially Gated", "Enterprise/Sales Gated", "Open Source / Local"
    ], f"Invalid self_serve value: {result.self_serve}"
    assert result.buildability in [
        "Easy (Ready today)", "Medium (App approval / OAuth required)",
        "Hard (Enterprise / Sales gated)", "Blocked (No public API)"
    ], f"Invalid buildability value: {result.buildability}"
    assert len(result.evidence_urls) > 0, "evidence_urls should not be empty"
    assert 0.0 <= result.confidence_score <= 1.0, f"Confidence score out of bounds: {result.confidence_score}"
    assert result.human_report_status is not None, "human_report_status should be preserved from disk cache!"

    print(f"  [PASS] Research completed in {elapsed:.2f}s:")
    print(f"    - Verdict:              {result.buildability}")
    print(f"    - Auth Methods:         {result.auth_methods}")
    print(f"    - Self-Serve:           {result.self_serve}")
    print(f"    - Existing MCP:         {result.existing_mcp} ({result.mcp_details})")
    print(f"    - Confidence:           {result.confidence_score}")
    print(f"    - Human Report Status:  {result.human_report_status}")
    print(f"    - Evidence URLs:        {result.evidence_urls[:2]}")
    return True


def test_analyze_patterns():
    print("\n--- [Step 7] Testing analyze_patterns() ---")
    from agent.analyzer import analyze_patterns

    analysis = analyze_patterns()
    assert isinstance(analysis, dict), f"Expected dict, got {type(analysis)}"

    # Required top-level metrics
    assert "total_apps" in analysis and analysis["total_apps"] > 0, "Missing total_apps"
    assert "composio_viable_count" in analysis, "Missing top-level composio_viable_count"
    assert "composio_viable_pct" in analysis, "Missing top-level composio_viable_pct"
    assert "greenfield_opportunity_pct" in analysis, "Missing top-level greenfield_opportunity_pct"

    # Required nested metrics for generate_html.py
    assert "buildability_breakdown" in analysis, "Missing buildability_breakdown"
    bb = analysis["buildability_breakdown"]
    assert "composio_viable_count" in bb, "Missing composio_viable_count in buildability_breakdown"
    assert "composio_viable_pct" in bb, "Missing composio_viable_pct in buildability_breakdown"

    assert "mcp_ecosystem" in analysis, "Missing mcp_ecosystem"
    mcp = analysis["mcp_ecosystem"]
    assert "greenfield_opportunity_pct" in mcp, "Missing greenfield_opportunity_pct in mcp_ecosystem"
    assert "greenfield_opportunity_count" in mcp, "Missing greenfield_opportunity_count in mcp_ecosystem"

    assert "product_ops_action_tiers" in analysis, "Missing product_ops_action_tiers"

    print("  [PASS] Analysis verified successfully:")
    print(f"    - Total Apps:            {analysis['total_apps']}")
    print(f"    - Composio Viable Count: {analysis['composio_viable_count']}")
    print(f"    - Composio Viable Pct:   {analysis['composio_viable_pct']}%")
    print(f"    - Greenfield Opp Pct:    {analysis['greenfield_opportunity_pct']}%")
    print(f"    - Existing MCP Count:    {mcp['existing_mcp_count']}")
    return True


def main():
    print("=" * 60)
    print("COMPOSIO THA PIPELINE & TOOLS VERIFICATION HARNESS")
    print("=" * 60)

    tests = [
        ("Environment Keys", test_environment_keys),
        ("Composio Client", test_composio_client),
        ("Web Search", test_search_web),
        ("Page Fetch", test_fetch_page),
        ("Telemetry Reporting", test_telemetry_reporting),
        ("Single-App Research", test_single_app_research),
        ("Pattern Analyzer", test_analyze_patterns),
    ]

    passed = 0
    failed = 0
    total_start = time.time()

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] FAILED: {name} -- {e}")
            failed += 1

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 60)
    print(f"SUMMARY: {passed}/{len(tests)} tests passed in {total_elapsed:.2f}s")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)
    else:
        print("ALL COMPOSIO TOOLS & PIPELINE CHECKS PASSED SUCCESSFULLY!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
