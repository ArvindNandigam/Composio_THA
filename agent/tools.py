import os
import httpx
from bs4 import BeautifulSoup
import urllib.parse
import base64
import re
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# COMPOSIO SDK & HOSTED MCP INTEGRATION PROVIDER
# ============================================================================
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID", "default")
COMPOSIO_MCP_URL = os.getenv("COMPOSIO_MCP_URL", "https://connect.composio.dev/mcp")
_composio_instance = None


def execute_composio_mcp(tool_slug: str, arguments: Dict[str, Any], timeout: float = 20.0) -> Optional[Dict[str, Any]]:
    """
    Executes a tool on Composio's hosted MCP gateway (https://connect.composio.dev/mcp)
    using the Consumer API Key (ck_...). Returns the parsed inner data response.
    """
    key = os.getenv("COMPOSIO_MCP_KEY") or os.getenv("COMPOSIO_API_KEY")
    if not key or not key.startswith("ck_"):
        return None
    headers = {
        "x-consumer-api-key": key,
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "COMPOSIO_MULTI_EXECUTE_TOOL",
            "arguments": {
                "tools": [
                    {
                        "tool_slug": tool_slug,
                        "arguments": arguments
                    }
                ]
            }
        }
    }
    try:
        import json
        r = httpx.post(COMPOSIO_MCP_URL, headers=headers, json=payload, timeout=timeout)
        if r.status_code == 200:
            for line in r.text.splitlines():
                if line.startswith("data: "):
                    parsed = json.loads(line[6:])
                    content = parsed.get("result", {}).get("content", [])
                    if content and content[0].get("text"):
                        inner = json.loads(content[0]["text"])
                        results = inner.get("data", {}).get("results", [])
                        if results:
                            return results[0].get("response", {}).get("data", {})
    except Exception as e:
        print(f"[Composio MCP Notice] {tool_slug} execution failed: {e}")
    return None


def get_composio_client():
    """
    Initializes and returns the Composio SDK client if COMPOSIO_API_KEY is configured.
    Provides direct tool execution via composio.tools.execute() with graceful fallback
    to direct httpx scrapers when unauthenticated or running offline.
    """
    global _composio_instance
    if _composio_instance is not None:
        return _composio_instance
    if not COMPOSIO_API_KEY:
        return None
    try:
        from composio import Composio
        _composio_instance = Composio(api_key=COMPOSIO_API_KEY)
        return _composio_instance
    except Exception as e:
        print(f"[Composio SDK Notice] Fallback to direct scrapers: {e}")
        return None


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

IGNORE_DOMAINS = [
    "wikipedia.org", "wiktionary.org", "facebook.com", "youtube.com/watch",
    "reddit.com", "quora.com", "tiktok.com", "instagram.com", "pinterest.com",
    "stackoverflow.com", "stackexchange.com", "medium.com", "dev.to",
    "twitter.com", "x.com"
]

KNOWN_MCP_REGISTRY = {
    "salesforce": {
        "exists": True,
        "details": "Official Salesforce DX MCP Server (@salesforce/mcp)",
        "url": "https://github.com/salesforcecli/mcp"
    },
    "github": {
        "exists": True,
        "details": "Official GitHub MCP Server (@modelcontextprotocol/server-github)",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/github"
    },
    "slack": {
        "exists": True,
        "details": "Official Slack MCP Server (@modelcontextprotocol/server-slack)",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/slack"
    },
    "notion": {
        "exists": True,
        "details": "Official & Community Notion MCP Server",
        "url": "https://github.com/michaellatman/mcp-notion"
    },
    "sentry": {
        "exists": True,
        "details": "Official Sentry MCP Server (getsentry/mcp-server-sentry)",
        "url": "https://github.com/getsentry/mcp-server-sentry"
    },
    "supabase": {
        "exists": True,
        "details": "Official Supabase MCP Server (supabase-community/mcp-server-supabase)",
        "url": "https://github.com/supabase-community/mcp-server-supabase"
    },
    "neo4j": {
        "exists": True,
        "details": "Official Neo4j MCP Server (neo4j-contrib/mcp-neo4j)",
        "url": "https://github.com/neo4j-contrib/mcp-neo4j"
    },
    "firecrawl": {
        "exists": True,
        "details": "Official Firecrawl MCP Server (mendableai/firecrawl-mcp-server)",
        "url": "https://github.com/mendableai/firecrawl-mcp-server"
    },
    "cloudflare": {
        "exists": True,
        "details": "Official Cloudflare MCP Server (cloudflare/mcp-server-cloudflare)",
        "url": "https://github.com/cloudflare/mcp-server-cloudflare"
    },
    "datadog": {
        "exists": True,
        "details": "Community Datadog MCP Server",
        "url": "https://github.com/datadog/mcp-server"
    },
    "devin": {
        "exists": True,
        "details": "Official Devin Native MCP Integration",
        "url": "https://docs.devin.ai/mcp"
    },
    "linear": {
        "exists": True,
        "details": "Official Community Linear MCP Server (@modelcontextprotocol/server-linear)",
        "url": "https://github.com/modelcontextprotocol/servers/tree/main/src/linear"
    },
    "airtable": {
        "exists": True,
        "details": "Community Airtable MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "jira": {
        "exists": True,
        "details": "Atlassian / Community Jira MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "stripe": {
        "exists": True,
        "details": "Official Stripe Agent Toolkit / MCP",
        "url": "https://github.com/stripe/agent-toolkit"
    },
    "otter ai": {
        "exists": True,
        "details": "Otter.ai MCP Community Integration",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "mermaid cli": {
        "exists": True,
        "details": "Mermaid Local CLI MCP Server (@mermaid-js/mermaid-cli)",
        "url": "https://github.com/mermaid-js/mermaid-cli"
    },
    "apify": {
        "exists": True,
        "details": "Official Apify Actors MCP Server (apify/actors-mcp-server)",
        "url": "https://github.com/apify/actors-mcp-server"
    },
    "bright data": {
        "exists": True,
        "details": "Official Bright Data Scraping MCP Server",
        "url": "https://github.com/luminati-io/brightdata-mcp"
    },
    "mongodb atlas": {
        "exists": True,
        "details": "Official MongoDB Atlas MCP Server",
        "url": "https://github.com/mongodb/mcp-server"
    },
    "sherlock": {
        "exists": True,
        "details": "Sherlock OSINT CLI (Local Subprocess MCP)",
        "url": "https://github.com/sherlock-project/sherlock"
    },
    "hubspot": {
        "exists": True,
        "details": "Community & Composio HubSpot MCP Server",
        "url": "https://github.com/ComposioHQ/composio"
    },
    "zendesk": {
        "exists": True,
        "details": "Community Zendesk MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "intercom": {
        "exists": True,
        "details": "Community Intercom MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "shopify": {
        "exists": True,
        "details": "Community Shopify MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "discord": {
        "exists": True,
        "details": "Community Discord MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "telegram": {
        "exists": True,
        "details": "Community Telegram MCP Server",
        "url": "https://github.com/modelcontextprotocol/servers"
    },
    "twenty": {
        "exists": True,
        "details": "Twenty Open-Source CRM MCP Server",
        "url": "https://github.com/twentyhq/twenty"
    },
    "posthog": {
        "exists": True,
        "details": "Community PostHog MCP Server",
        "url": "https://github.com/posthog/mcp-server"
    },
    "resend": {
        "exists": True,
        "details": "Community Resend MCP Server",
        "url": "https://github.com/resend/mcp-server"
    }
}


def decode_bing_url(u_param: str) -> str:
    """Decodes Bing redirect parameter to extract actual destination URL."""
    try:
        if u_param.startswith("a1"):
            b64_str = u_param[2:]
            b64_str += '=' * (-len(b64_str) % 4)
            return base64.b64decode(b64_str).decode('utf-8', errors='ignore')
        return u_param
    except Exception:
        return u_param


def is_valid_evidence_url(url: str, app_name: str, hint: str) -> bool:
    """Filters out irrelevant generic links (Wikipedia, generic social)."""
    if not url or not url.startswith("http"):
        return False
    lower_url = url.lower()
    for d in IGNORE_DOMAINS:
        if d in lower_url and d not in hint.lower():
            return False
    return True


def _extract_composio_search_results(
    resp: Any, max_results: int, app_name: str, hint: str
) -> List[Dict[str, str]]:
    """Normalizes Composio tool execution output into standard search result dicts."""
    data = resp.get("data", resp) if isinstance(resp, dict) else getattr(resp, "data", resp)
    if not isinstance(data, dict):
        return []

    raw_items = (
        data.get("results")
        or data.get("organic_results")
        or data.get("data")
        or []
    )
    if not isinstance(raw_items, list):
        return []

    parsed: List[Dict[str, str]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        dest_url = item.get("url") or item.get("link") or ""
        if not is_valid_evidence_url(dest_url, app_name, hint):
            continue
        parsed.append({
            "title": str(item.get("title", "")).strip(),
            "url": dest_url,
            "snippet": str(item.get("content") or item.get("snippet") or item.get("description") or "").strip(),
        })
        if len(parsed) >= max_results:
            break
    return parsed


def search_web(query: str, max_results: int = 4, app_name: str = "", hint: str = "") -> List[Dict[str, str]]:
    """
    Executes web search with multi-tier execution:
    1. Composio Hosted MCP Server (connect.composio.dev/mcp) via Consumer API Key (ck_...)
    2. Composio Python SDK (via Project API Key ak_...)
    3. Direct Tavily REST API (if TAVILY_API_KEY configured)
    4. Resilient direct Bing search fallback.
    """
    search_slug = os.getenv("COMPOSIO_SEARCH_SLUG", "TAVILY_SEARCH")

    # Tier 1: Composio Hosted MCP Gateway
    mcp_resp = execute_composio_mcp(search_slug, {"query": query, "max_results": max_results})
    if mcp_resp:
        mcp_results = []
        for item in mcp_resp.get("results", []):
            u = item.get("url", "")
            if is_valid_evidence_url(u, app_name, hint):
                mcp_results.append({
                    "title": item.get("title", ""),
                    "url": u,
                    "snippet": item.get("content", "")
                })
        if mcp_results:
            return mcp_results[:max_results]

    # Tier 2: Composio Python SDK
    composio = get_composio_client()
    if composio is not None:
        try:
            resp = composio.tools.execute(
                slug=search_slug,
                arguments={"query": query, "max_results": max_results},
                user_id=COMPOSIO_USER_ID,
                dangerously_skip_version_check=True,
            )
            composio_results = _extract_composio_search_results(resp, max_results, app_name, hint)
            if composio_results:
                return composio_results
        except Exception as e:
            print(f"[Composio SDK Notice] {search_slug} failed ({e}); checking direct providers.")

    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            resp = httpx.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "max_results": max_results},
                timeout=10.0
            )
            if resp.status_code == 200:
                tav_data = resp.json()
                tav_results = []
                for item in tav_data.get("results", []):
                    u = item.get("url", "")
                    if is_valid_evidence_url(u, app_name, hint):
                        tav_results.append({
                            "title": item.get("title", ""),
                            "url": u,
                            "snippet": item.get("content", "")
                        })
                if tav_results:
                    return tav_results[:max_results]
        except Exception as e:
            print(f"[Tavily Direct Notice] Direct Tavily call failed ({e}); falling back to Bing.")

    url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
    try:
        resp = httpx.get(url, headers=DEFAULT_HEADERS, timeout=8.0, follow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for li in soup.find_all("li", class_="b_algo"):
            h2 = li.find("h2")
            if h2 and h2.find("a"):
                a = h2.find("a")
                raw_href = a.get("href", "")

                dest_url = raw_href
                if "bing.com/ck/a" in raw_href:
                    parsed = urllib.parse.urlparse(raw_href)
                    params = urllib.parse.parse_qs(parsed.query)
                    if "u" in params and params["u"]:
                        dest_url = decode_bing_url(params["u"][0])

                if not is_valid_evidence_url(dest_url, app_name, hint):
                    continue

                p = li.find("p")
                snippet = p.get_text(strip=True) if p else ""
                title = a.get_text(strip=True)

                results.append({
                    "title": title,
                    "url": dest_url,
                    "snippet": snippet
                })
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Search failed: {e}"}]


def fetch_page(url: str, max_chars: int = 3000) -> str:
    """
    Fetches documentation text with multi-tier execution:
    1. Composio Hosted MCP Server (connect.composio.dev/mcp) via Consumer API Key (ck_...)
    2. Composio Python SDK (via Project API Key ak_...)
    3. Direct Firecrawl Scrape API (if FIRECRAWL_API_KEY configured)
    4. Resilient httpx + BeautifulSoup extraction.
    """
    if not url or not url.startswith("http"):
        return ""

    fetch_slug = os.getenv("COMPOSIO_FETCH_SLUG", "FIRECRAWL_SCRAPE")

    # Tier 1: Composio Hosted MCP Gateway
    mcp_resp = execute_composio_mcp(fetch_slug, {"url": url})
    if mcp_resp:
        data = mcp_resp.get("data", {})
        content = data.get("markdown") or data.get("content") or ""
        if content:
            cleaned = re.sub(r'\s+', ' ', content.strip())
            return cleaned[:max_chars]

    # Tier 2: Composio Python SDK
    composio = get_composio_client()
    if composio is not None:
        try:
            resp = composio.tools.execute(
                slug=fetch_slug,
                arguments={"url": url},
                user_id=COMPOSIO_USER_ID,
                dangerously_skip_version_check=True,
            )
            data = resp.get("data", resp) if isinstance(resp, dict) else getattr(resp, "data", resp)
            if isinstance(data, dict):
                content = data.get("markdown") or data.get("content") or data.get("text") or ""
                if isinstance(content, str) and content.strip():
                    cleaned = re.sub(r'\s+', ' ', content.strip())
                    return cleaned[:max_chars]
        except Exception as e:
            print(f"[Composio SDK Notice] {fetch_slug} failed ({e}); checking direct providers.")

    firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
    if firecrawl_key:
        try:
            fc_resp = httpx.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={"Authorization": f"Bearer {firecrawl_key}"},
                json={"url": url},
                timeout=12.0
            )
            if fc_resp.status_code == 200:
                fc_data = fc_resp.json().get("data", {})
                content = fc_data.get("markdown") or fc_data.get("content") or ""
                if content:
                    cleaned = re.sub(r'\s+', ' ', content.strip())
                    return cleaned[:max_chars]
        except Exception as e:
            print(f"[Firecrawl Direct Notice] Direct Firecrawl call failed ({e}); falling back to httpx.")

    try:
        resp = httpx.get(url, headers=DEFAULT_HEADERS, timeout=7.0, follow_redirects=True)
        if resp.status_code >= 400:
            return f"HTTP {resp.status_code} Error"

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text[:max_chars]
    except Exception as e:
        return f"Fetch error: {e}"


def verify_url(url: str) -> bool:
    """Checks if a URL is reachable."""
    if not url or not url.startswith("http"):
        return False
    try:
        resp = httpx.head(url, headers=DEFAULT_HEADERS, timeout=5.0, follow_redirects=True)
        if resp.status_code < 400:
            return True
        resp = httpx.get(url, headers=DEFAULT_HEADERS, timeout=5.0, follow_redirects=True)
        return resp.status_code < 400
    except Exception:
        return False


def check_mcp_support(app_name: str) -> Dict[str, Any]:
    """Checks if there is a known MCP server for this app."""
    key = app_name.strip().lower()
    if key in KNOWN_MCP_REGISTRY:
        return KNOWN_MCP_REGISTRY[key]
    for k, v in KNOWN_MCP_REGISTRY.items():
        if k in key or key in k:
            return v
    return {"exists": False, "details": "None known", "url": None}
