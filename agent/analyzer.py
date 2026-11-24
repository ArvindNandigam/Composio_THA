import os
import json
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "research_results.json")
ANALYSIS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "analysis_results.json")
TELEMETRY_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "telemetry_metrics.json")

def analyze_patterns(results_path: Optional[str] = None) -> Dict[str, Any]:
    """Analyzes the 100-app dataset to extract statistical patterns and Product Ops insights."""
    target_file = results_path or RESULTS_FILE
    if not os.path.exists(target_file):
        print(f"Results file {target_file} not found!")
        return {}

    with open(target_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_apps = len(data)
    print(f"Running pattern analysis across {total_apps} apps...")

    # 1. Auth Distribution (deduplicated per app so each app counts once per normalized protocol)
    auth_counter = Counter()
    for app in data:
        app_auth_cats = set()
        for m in app.get("auth_methods", []):
            # Normalize auth strings
            m_norm = m.strip().lower()
            if "oauth" in m_norm:
                app_auth_cats.add("OAuth2")
            elif "api key" in m_norm or "apikey" in m_norm:
                app_auth_cats.add("API Key")
            elif "token" in m_norm or "bearer" in m_norm or "pat" in m_norm:
                app_auth_cats.add("Personal / Access Token")
            elif "basic" in m_norm:
                app_auth_cats.add("Basic Auth")
            elif "cli" in m_norm or "none" in m_norm:
                app_auth_cats.add("No Auth (Local CLI)")
            else:
                app_auth_cats.add("Other / Custom")
        for cat in app_auth_cats:
            auth_counter[cat] += 1

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
    tier3_partner_outreach = [] # Enterprise/Sales gated or Blocked (No public API)
    tier4_cli_mcp = []          # Local CLI / Open source

    for app in data:
        name = app.get("name")
        b = app.get("buildability", "")
        g = app.get("self_serve", "")
        auth = app.get("auth_methods", [])

        if any("cli" in a.lower() or "none" in a.lower() for a in auth) or g == "Open Source / Local":
            tier4_cli_mcp.append({"id": app["id"], "name": name, "category": app["category"], "reason": "Local CLI tool / Open source; zero API auth needed"})
        elif "Blocked" in b or "Hard" in b or "Enterprise" in g:
            tier3_partner_outreach.append({"id": app["id"], "name": name, "category": app["category"], "reason": (app.get("blocker_analysis") or "")[:100]})
        elif "Easy" in b and ("Self-serve" in g or "Open Source" in g):
            tier1_quick_wins.append({"id": app["id"], "name": name, "category": app["category"], "reason": "Self-serve signup, public API, instant developer access"})
        else:
            tier2_oauth_builds.append({"id": app["id"], "name": name, "category": app["category"], "reason": "OAuth2 application registration / scope permissions needed"})

    # 7. MCP Ecosystem Statistics
    existing_mcp_count = sum(1 for app in data if app.get("existing_mcp", False))
    existing_mcp_pct = round(existing_mcp_count / total_apps * 100, 1) if total_apps > 0 else 0.0
    greenfield_opportunity_count = total_apps - existing_mcp_count
    greenfield_opportunity_pct = round(greenfield_opportunity_count / total_apps * 100, 1) if total_apps > 0 else 0.0

    # Buildability Composio Viability (Easy + Medium)
    easy_count = sum(cnt for b, cnt in buildability_counter.items() if "easy" in b.lower())
    medium_count = sum(cnt for b, cnt in buildability_counter.items() if "medium" in b.lower())
    hard_count = sum(cnt for b, cnt in buildability_counter.items() if "hard" in b.lower())
    blocked_count = sum(cnt for b, cnt in buildability_counter.items() if "blocked" in b.lower())
    composio_viable_count = easy_count + medium_count
    composio_viable_pct = round(composio_viable_count / total_apps * 100, 1) if total_apps > 0 else 0.0

    auth_pcts = {k: round(v / total_apps * 100, 1) for k, v in auth_counter.items()} if total_apps > 0 else {}
    oauth_or_key_count = sum(
        1 for app in data
        if any("oauth" in m.lower() or "api key" in m.lower() or "apikey" in m.lower() for m in app.get("auth_methods", []))
    )
    oauth_or_key_pct = round(oauth_or_key_count / total_apps * 100, 1) if total_apps > 0 else 0.0

    frictionless_count = gating_counter.get("Self-serve", 0) + gating_counter.get("Open Source / Local", 0)
    frictionless_pct = round(frictionless_count / total_apps * 100, 1) if total_apps > 0 else 0.0
    top_open_cats = sorted(category_summary.items(), key=lambda x: (-x[1]["self_serve_pct"], x[0]))
    top_gated_cats = sorted(category_summary.items(), key=lambda x: (-x[1]["gated_pct"], x[0]))
    if len(top_open_cats) >= 2 and len(top_gated_cats) >= 2:
        c1, d1 = top_open_cats[0]
        c2, d2 = top_open_cats[1]
        g1, gd1 = top_gated_cats[0]
        g2, gd2 = top_gated_cats[1]
        gating_insight = (
            f"Category gating polarization ({frictionless_pct}% frictionless overall): "
            f"{c1} ({d1['self_serve_pct']}% self-serve) and {c2} ({d2['self_serve_pct']}% self-serve) "
            f"lead open onboarding, whereas {g1} ({gd1['gated_pct']}% gated) and {g2} ({gd2['gated_pct']}% gated) "
            f"show the highest gating friction."
        )
    else:
        gating_insight = f"Category gating overview: {frictionless_pct}% ({frictionless_count}/{total_apps}) offer frictionless self-serve or local access."

    admin_gated_count = medium_count + hard_count
    admin_gated_pct = round(admin_gated_count / total_apps * 100, 1) if total_apps > 0 else 0.0
    blocked_pct = round(blocked_count / total_apps * 100, 1) if total_apps > 0 else 0.0

    cli_count = len(tier4_cli_mcp)
    if cli_count > 0:
        cli_names = ", ".join(item["name"] for item in tier4_cli_mcp[:3])
        cli_insight = (
            f"Local CLI & Open-Source Tools ({cli_count} apps, e.g., {cli_names}) require a distinct "
            f"local MCP subprocess paradigm (stdio/containerized workers) rather than cloud HTTP webhooks."
        )
    else:
        cli_insight = "All analyzed platforms expose remote HTTP/cloud endpoints without local CLI subprocess requirements."

    headline_insights = [
        (
            f"OAuth2 ({auth_pcts.get('OAuth2', 0.0)}%) and API Keys ({auth_pcts.get('API Key', 0.0)}%) cover "
            f"{oauth_or_key_pct}% of the {total_apps} platforms ({oauth_or_key_count}/{total_apps}), with "
            f"Personal/Access Tokens at {auth_pcts.get('Personal / Access Token', 0.0)}% and Basic Auth at {auth_pcts.get('Basic Auth', 0.0)}%."
        ),
        gating_insight,
        (
            f"Primary non-technical friction: {admin_gated_count}/{total_apps} ({admin_gated_pct}%) require "
            f"administrative approval ({medium_count} OAuth app review + {hard_count} enterprise/sales contracts), "
            f"alongside {blocked_count} ({blocked_pct}%) blocked without a public API -- leaving "
            f"{composio_viable_count}/{total_apps} ({composio_viable_pct}%) Composio-viable today."
        ),
        (
            f"MCP Greenfield Opportunity: {existing_mcp_count}/{total_apps} ({existing_mcp_pct}%) have a verified "
            f"official or community MCP server, leaving {greenfield_opportunity_count}/{total_apps} "
            f"({greenfield_opportunity_pct}%) as greenfield opportunities for Composio."
        ),
        cli_insight
    ]

    analysis = {
        "dataset_metadata": {
            "total_apps": total_apps,
            "categories_count": len(category_summary)
        },
        "total_apps": total_apps,
        "composio_viable_count": composio_viable_count,
        "composio_viable_pct": composio_viable_pct,
        "greenfield_opportunity_count": greenfield_opportunity_count,
        "greenfield_opportunity_pct": greenfield_opportunity_pct,
        "auth_distribution": {
            "counts": dict(auth_counter),
            "percentages": {k: round(v / total_apps * 100, 1) for k, v in auth_counter.items()} if total_apps > 0 else {},
            "calculation_note": f"Percentage of total {total_apps} apps supporting each protocol (deduplicated per app per bucket). Apps supporting multiple distinct mechanisms (e.g. OAuth2 + API Key) count in each."
        },
        "auth_breakdown": dict(auth_counter),
        "gating_distribution": {
            "counts": dict(gating_counter),
            "percentages": {k: round(v / total_apps * 100, 1) for k, v in gating_counter.items()}
        },
        "category_matrix": category_summary,
        "category_breakdown": category_summary,
        "buildability_breakdown": {
            "counts": dict(buildability_counter),
            "percentages": {k: round(v / total_apps * 100, 1) for k, v in buildability_counter.items()},
            "composio_viable_count": composio_viable_count,
            "composio_viable_pct": composio_viable_pct,
            "calculation_note": f"Easy ({easy_count}) + Medium ({medium_count}) = {composio_viable_count} ({composio_viable_pct}%) Composio viable today without enterprise sales contracts."
        },
        "top_blockers": dict(blocker_categories.most_common()),
        "mcp_ecosystem": {
            "existing_mcp_count": existing_mcp_count,
            "existing_mcp_pct": round(existing_mcp_count / total_apps * 100, 1) if total_apps > 0 else 0.0,
            "greenfield_opportunity_count": greenfield_opportunity_count,
            "greenfield_opportunity_pct": greenfield_opportunity_pct,
            "calculation_note": f"{existing_mcp_count} verified official/community MCP servers ({round(existing_mcp_count / total_apps * 100, 1) if total_apps > 0 else 0.0}%), leaving {greenfield_opportunity_count} greenfield opportunities ({greenfield_opportunity_pct}%)."
        },
        "mcp_breakdown": {
            "existing_mcp_count": existing_mcp_count,
            "greenfield_opportunity_count": greenfield_opportunity_count,
            "greenfield_opportunity_pct": greenfield_opportunity_pct
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
                "description": "Enterprise/partner gated or blocked (no public API): requires sales contracts, BYO credentials, or is closed-ecosystem.",
                "sample": tier3_partner_outreach[:8]
            },
            "tier4_cli_mcp": {
                "count": len(tier4_cli_mcp),
                "description": "Open source / CLI tools: best exposed as local MCP servers or containerized workers.",
                "sample": tier4_cli_mcp
            }
        },
        "headline_insights": headline_insights,
        "patterns": headline_insights
    }

    # Ingest Composio telemetry metrics
    telemetry_metrics = {}
    if os.path.exists(TELEMETRY_FILE):
        try:
            with open(TELEMETRY_FILE, "r", encoding="utf-8") as tf:
                t_raw = json.load(tf)
                telemetry_metrics = {
                    "total_queries": t_raw.get("total_queries", 0),
                    "composio_queries": t_raw.get("composio_queries", 0),
                    "fallback_queries": t_raw.get("fallback_queries", 0),
                    "composio_share_pct": t_raw.get("composio_share_pct", 0.0),
                    "composio_search": t_raw.get("composio_search", 0),
                    "composio_fetch": t_raw.get("composio_fetch", 0),
                    "fallback_search": t_raw.get("fallback_search", 0),
                    "fallback_fetch": t_raw.get("fallback_fetch", 0),
                    "by_tool": t_raw.get("by_tool", {}),
                    "providers": t_raw.get("providers", {})
                }
        except Exception as e:
            print(f"Warning loading telemetry metrics: {e}")

    analysis["telemetry_metrics"] = telemetry_metrics
    analysis["telemetry"] = telemetry_metrics

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)

    print(f"Pattern analysis completed and saved to {ANALYSIS_FILE}")
    return analysis

if __name__ == "__main__":
    analyze_patterns()
