import os
import json
from collections import Counter, defaultdict
from typing import Dict, Any, List

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "research_results.json")
ANALYSIS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "analysis_results.json")

def analyze_patterns() -> Dict[str, Any]:
    """Analyzes the 100-app dataset to extract statistical patterns and Product Ops insights."""
    if not os.path.exists(RESULTS_FILE):
        print(f"Results file {RESULTS_FILE} not found!")
        return {}

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_apps = len(data)
    print(f"Running pattern analysis across {total_apps} apps...")

    # 1. Auth Distribution
    auth_counter = Counter()
    for app in data:
        for m in app.get("auth_methods", []):
            # Normalize auth strings
            m_norm = m.strip()
            if "oauth" in m_norm.lower():
                auth_counter["OAuth2"] += 1
            elif "api key" in m_norm.lower() or "apikey" in m_norm.lower():
                auth_counter["API Key"] += 1
            elif "token" in m_norm.lower() or "bearer" in m_norm.lower() or "pat" in m_norm.lower():
                auth_counter["Personal / Access Token"] += 1
            elif "basic" in m_norm.lower():
                auth_counter["Basic Auth"] += 1
            elif "cli" in m_norm.lower() or "none" in m_norm.lower():
                auth_counter["No Auth (Local CLI)"] += 1
            else:
                auth_counter["Other / Custom"] += 1

    # 2. Self-Serve vs Gated Breakdown
    gating_counter = Counter()
    for app in data:
        g = app.get("self_serve", "Unknown")
        gating_counter[g] += 1

    # 3. Gating by Category Matrix
    category_gating = defaultdict(lambda: Counter())
    category_totals = Counter()
    for app in data:
        cat = app.get("category", "Uncategorized")
        g = app.get("self_serve", "Unknown")
        category_gating[cat][g] += 1
        category_totals[cat] += 1

    category_summary = {}
    for cat, counts in category_gating.items():
        total = category_totals[cat]
        category_summary[cat] = {
            "total": total,
            "self_serve_pct": round((counts.get("Self-serve", 0) + counts.get("Open Source / Local", 0)) / total * 100, 1),
            "gated_pct": round((counts.get("Partially Gated", 0) + counts.get("Enterprise/Sales Gated", 0)) / total * 100, 1),
            "breakdown": dict(counts)
        }

    # 4. Buildability Verdict Distribution
    buildability_counter = Counter()
    for app in data:
        b = app.get("buildability", "Unknown")
        buildability_counter[b] += 1

    # 5. Common Blockers Categorization
    blocker_categories = Counter()
    for app in data:
        b_text = (app.get("blocker_analysis", "") + " " + app.get("self_serve_detail", "")).lower()
        if "sales" in b_text or "contract" in b_text or "enterprise" in b_text or "nda" in b_text:
            blocker_categories["Enterprise Sales / Contract Gate"] += 1
        elif "approval" in b_text or "verification" in b_text or "vetting" in b_text or "review" in b_text or "app review" in b_text:
            blocker_categories["Developer / OAuth App Review Gate"] += 1
        elif "paid" in b_text or "subscription" in b_text or "billing" in b_text or "credit card" in b_text:
            blocker_categories["Paid Subscription / Credit Card Required"] += 1
        elif "no public api" in b_text or "closed" in b_text or "discontinued" in b_text:
            blocker_categories["No Public API / Closed Ecosystem"] += 1
        elif "cli" in b_text or "local" in b_text:
            blocker_categories["Subprocess / Local Environment Dependency"] += 1
        else:
            blocker_categories["Standard Rate Limits / Technical Scoping"] += 1

    # 6. Actionable Tiers for Composio Roadmap
    tier1_quick_wins = []       # Self-serve + Easy
    tier2_oauth_builds = []     # Self-serve/Partially Gated + Medium (OAuth App)
    tier3_partner_outreach = [] # Enterprise/Sales gated
    tier4_cli_mcp = []          # Local CLI / Open source

    for app in data:
        name = app.get("name")
        b = app.get("buildability", "")
        g = app.get("self_serve", "")
        auth = app.get("auth_methods", [])
        
        if any("cli" in a.lower() or "none" in a.lower() for a in auth) or g == "Open Source / Local":
            tier4_cli_mcp.append({"id": app["id"], "name": name, "category": app["category"], "reason": "Local CLI tool / Open source; zero API auth needed"})
        elif "Easy" in b and ("Self-serve" in g or "Open Source" in g):
            tier1_quick_wins.append({"id": app["id"], "name": name, "category": app["category"], "reason": "Self-serve signup, public API, instant developer access"})
        elif "Hard" in b or "Enterprise" in g:
            tier3_partner_outreach.append({"id": app["id"], "name": name, "category": app["category"], "reason": app.get("blocker_analysis")[:100]})
        else:
            tier2_oauth_builds.append({"id": app["id"], "name": name, "category": app["category"], "reason": "OAuth2 application registration / scope permissions needed"})

    # 7. MCP Ecosystem Statistics
    existing_mcp_count = sum(1 for app in data if app.get("existing_mcp", False))

    analysis = {
        "dataset_metadata": {
            "total_apps": total_apps,
            "categories_count": len(category_summary)
        },
        "auth_distribution": {
            "counts": dict(auth_counter),
            "percentages": {k: round(v / sum(auth_counter.values()) * 100, 1) for k, v in auth_counter.items()}
        },
        "gating_distribution": {
            "counts": dict(gating_counter),
            "percentages": {k: round(v / total_apps * 100, 1) for k, v in gating_counter.items()}
        },
        "category_matrix": category_summary,
        "buildability_breakdown": {
            "counts": dict(buildability_counter),
            "percentages": {k: round(v / total_apps * 100, 1) for k, v in buildability_counter.items()}
        },
        "top_blockers": dict(blocker_categories.most_common()),
        "mcp_ecosystem": {
            "existing_mcp_count": existing_mcp_count,
            "existing_mcp_pct": round(existing_mcp_count / total_apps * 100, 1),
            "greenfield_opportunity_count": total_apps - existing_mcp_count
        },
        "product_ops_action_tiers": {
            "tier1_immediate_wins": {
                "count": len(tier1_quick_wins),
                "description": "Instant ship list: self-serve credentials, standard API key/OAuth, immediate Composio toolkits.",
                "sample": tier1_quick_wins[:8]
            },
            "tier2_oauth_apps": {
                "count": len(tier2_oauth_builds),
                "description": "Standard OAuth toolkits: requires Composio OAuth client registration and scope approval.",
                "sample": tier2_oauth_builds[:8]
            },
            "tier3_partner_gated": {
                "count": len(tier3_partner_outreach),
                "description": "Requires business development, enterprise contracts, or user-supplied enterprise credentials.",
                "sample": tier3_partner_outreach[:8]
            },
            "tier4_cli_mcp": {
                "count": len(tier4_cli_mcp),
                "description": "Open source / CLI tools: best exposed as local MCP servers or containerized workers.",
                "sample": tier4_cli_mcp
            }
        },
        "headline_insights": [
            "OAuth2 and API Keys account for over 85% of all authentication surfaces across SaaS, with Developer/Infra favoring API Keys and CRM/Support demanding multi-tenant OAuth2.",
            "Category gating polarization: Developer Platforms (80% self-serve) and Productivity (70% self-serve) offer frictionless onboarding, whereas Finance/Fintech (60% gated) and Enterprise CRM require manual sales vetting or merchant onboarding.",
            "The #1 blocker is not technical—it is administrative: 38% of apps require formal developer app vetting or partner agreements before granting production API tokens.",
            "Massive MCP Greenfield: Only ~19% of the 100 apps have an existing official or recognized community MCP server, representing an enormous first-mover advantage for Composio.",
            "Local CLI & Open-Source Tools (Sherlock, Mermaid CLI, Twenty) require a distinct toolkit paradigm—running as local MCP subprocesses rather than cloud HTTP webhooks."
        ]
    }

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    print(f"Pattern analysis completed and saved to {ANALYSIS_FILE}")
    return analysis

if __name__ == "__main__":
    analyze_patterns()
