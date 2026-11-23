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
# COMPOSIO SDK INTEGRATION PROVIDER
# ============================================================================
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
_composio_instance = None

def get_composio_client():
    """
    Initializes and returns the Composio SDK client if COMPOSIO_API_KEY is configured.
    Provides agent tool routing, managed OAuth integrations, and MCP execution.
    Falls back gracefully to direct scrapers when unauthenticated or running offline.
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

# Domains to filter out from evidence URLs (blacklist unofficial and forum sites)
IGNORE_DOMAINS = [
    "wikipedia.org", "wiktionary.org", "facebook.com", "youtube.com/watch",
    "reddit.com", "quora.com", "tiktok.com", "instagram.com", "pinterest.com",
    "stackoverflow.com", "stackexchange.com", "medium.com", "dev.to",
    "twitter.com", "x.com"
]

# Curated reference map of established MCP servers (Official & Authoritative Community)
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

def search_web(query: str, max_results: int = 4, app_name: str = "", hint: str = "") -> List[Dict[str, str]]:
    """Performs web search via Bing web endpoint with decoded URLs and extracted snippets."""
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
    """Fetches text content from a given documentation URL."""
    if not url or not url.startswith("http"):
        return ""
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
