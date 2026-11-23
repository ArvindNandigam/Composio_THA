import httpx
from bs4 import BeautifulSoup
import urllib.parse
import base64
import re
from typing import List, Dict, Any, Optional

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}

# Domains to filter out from evidence URLs
IGNORE_DOMAINS = [
    "wikipedia.org", "wiktionary.org", "facebook.com/policies", "youtube.com/watch",
    "reddit.com", "quora.com", "tiktok.com", "instagram.com", "pinterest.com"
]

# Curated reference map of established MCP servers (Official & Community)
KNOWN_MCP_REGISTRY = {
    "github": {"exists": True, "details": "Official GitHub MCP Server (@modelcontextprotocol/server-github)"},
    "slack": {"exists": True, "details": "Official Slack MCP Server (@modelcontextprotocol/server-slack)"},
    "notion": {"exists": True, "details": "Community & Composio Notion MCP Server"},
    "sentry": {"exists": True, "details": "Official Sentry MCP Server (getsentry/mcp-server-sentry)"},
    "supabase": {"exists": True, "details": "Official Supabase MCP Server (supabase/mcp-server-supabase)"},
    "neo4j": {"exists": True, "details": "Official Neo4j MCP Server (neo4j-contrib/mcp-neo4j)"},
    "firecrawl": {"exists": True, "details": "Official Firecrawl MCP Server (mendableai/firecrawl-mcp-server)"},
    "cloudflare": {"exists": True, "details": "Official Cloudflare MCP Server (cloudflare/mcp-server-cloudflare)"},
    "datadog": {"exists": True, "details": "Community Datadog MCP Server (datadog-mcp)"},
    "devin": {"exists": True, "details": "Devin native MCP client / server integrations"},
    "linear": {"exists": True, "details": "Community Linear MCP Server (@modelcontextprotocol/server-linear)"},
    "airtable": {"exists": True, "details": "Community Airtable MCP Server"},
    "jira": {"exists": True, "details": "Atlassian / Community Jira MCP Server"},
    "stripe": {"exists": True, "details": "Official Stripe Agent Toolkit / Community MCP"},
    "otter ai": {"exists": True, "details": "Otter MCP community integrations"},
    "mermaid cli": {"exists": True, "details": "Mermaid local CLI / MCP wrapper (@mermaid-js/mermaid-cli)"},
    "apify": {"exists": True, "details": "Official Apify Actors MCP Server (apify/actors-mcp-server)"},
    "bright data": {"exists": True, "details": "Official Bright Data Scraping MCP Server"},
    "mongodb atlas": {"exists": True, "details": "Official MongoDB MCP Server"}
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
    return {"exists": False, "details": "None known"}
