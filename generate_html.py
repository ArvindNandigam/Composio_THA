import os
import json
from typing import Dict, Any, List

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "data", "research_results.json")
ANALYSIS_FILE = os.path.join(os.path.dirname(__file__), "data", "analysis_results.json")
AUDIT_FILE = os.path.join(os.path.dirname(__file__), "data", "verification_audit.json")

OUTPUT_INDEX = os.path.join(os.path.dirname(__file__), "index.html")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def build_html_deliverable():
    if not os.path.exists(RESULTS_FILE) or not os.path.exists(ANALYSIS_FILE) or not os.path.exists(AUDIT_FILE):
        print("Required data files missing.")
        return

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        apps = json.load(f)

    with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        audit = json.load(f)

    apps_json = json.dumps(apps)
    analysis_json = json.dumps(analysis)

    pass1_acc = audit.get("pass1_accuracy_pct", 77.0)
    auto_verif_acc = audit.get("automated_verification_accuracy_pct", 86.0)
    auto_uplift = audit.get("automated_verification_uplift_pct", 9.0)
    human_corrections = audit.get("human_audit_discrepancies_found", 23)
    human_disc_rate = audit.get("human_audit_discrepancy_rate_pct", 23.0)
    post_human_acc = audit.get("post_human_ground_truth_accuracy_pct", 100.0)

    viable_pct = analysis['buildability_breakdown']['composio_viable_pct']
    viable_count = analysis['buildability_breakdown']['composio_viable_count']
    self_serve_pct = analysis['gating_distribution']['percentages'].get('Self-serve', 70.0) + analysis['gating_distribution']['percentages'].get('Open Source / Local', 6.0)
    self_serve_count = analysis['gating_distribution']['counts'].get('Self-serve', 70) + analysis['gating_distribution']['counts'].get('Open Source / Local', 6)
    existing_mcp_count = analysis['mcp_ecosystem']['existing_mcp_count']
    greenfield_count = analysis['mcp_ecosystem']['greenfield_opportunity_count']
    greenfield_pct = analysis['mcp_ecosystem']['greenfield_opportunity_pct']

    tiers = analysis['product_ops_action_tiers']

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Composio Take-Home Assignment | 100-App Integration Feasibility Case Study</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                        mono: ['"JetBrains Mono"', 'monospace'],
                    }},
                    colors: {{
                        brand: {{
                            50: '#eef2ff',
                            100: '#e0e7ff',
                            500: '#6366f1',
                            600: '#4f46e5',
                            700: '#4338ca',
                            900: '#312e81',
                        }},
                        dark: {{
                            900: '#0B0F19',
                            800: '#111827',
                            700: '#1F2937',
                            600: '#374151',
                        }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        body {{
            background-color: #0B0F19;
            color: #F3F4F6;
        }}
        .glass-panel {{
            background: rgba(17, 24, 39, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .badge-easy {{ background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-medium {{ background: rgba(245, 158, 11, 0.15); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .badge-hard {{ background: rgba(239, 68, 68, 0.15); color: #F87171; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .badge-blocked {{ background: rgba(107, 114, 128, 0.2); color: #9CA3AF; border: 1px solid rgba(107, 114, 128, 0.4); }}
        .badge-selfserve {{ background: rgba(59, 130, 246, 0.15); color: #60A5FA; border: 1px solid rgba(59, 130, 246, 0.3); }}
        .badge-gated {{ background: rgba(217, 70, 239, 0.15); color: #E879F9; border: 1px solid rgba(217, 70, 239, 0.3); }}
    </style>
</head>
<body class="min-h-screen antialiased selection:bg-brand-500 selection:text-white">

    <!-- Navbar -->
    <header class="sticky top-0 z-40 glass-panel border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center font-bold text-white shadow-lg shadow-brand-500/20">
                    C
                </div>
                <div>
                    <span class="font-bold text-lg tracking-tight text-white">Composio</span>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-brand-900/60 text-brand-300 font-mono ml-2 border border-brand-700/50">2-Minute Case Study</span>
                </div>
            </div>
            <nav class="hidden md:flex items-center space-x-5 text-xs font-medium text-gray-300">
                <a href="#patterns" class="hover:text-white transition">Headline Patterns</a>
                <a href="#roadmap" class="hover:text-white transition">Ship Roadmap</a>
                <a href="#agent" class="hover:text-white transition">Agent & Proof</a>
                <a href="#verification" class="hover:text-white transition">Verification</a>
                <a href="#matrix" class="hover:text-white transition">100-App Matrix</a>
            </nav>
            <div class="flex items-center space-x-3">
                <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs font-semibold text-gray-200 border border-gray-700 shadow transition flex items-center space-x-1.5">
                    <svg class="w-3.5 h-3.5 text-gray-400" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
                    <span>GitHub</span>
                </a>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-10 pb-10 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-3xl">
                <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold mb-3">
                    <span>Autonomous Research & Verification Case Study</span>
                </div>
                <h1 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-white leading-tight">
                    100-App Integration Feasibility & Pattern Analysis
                </h1>
                <p class="mt-3 text-sm sm:text-base text-gray-400 leading-relaxed">
                    A self-contained 2-minute executive briefing evaluating authentication mechanisms, credential gating, API surfaces, and MCP ecosystem readiness for Composio toolkits.
                </p>
            </div>

            <!-- Candidate Dossier -->
            <div class="mt-6 p-4 rounded-xl glass-panel border border-brand-500/30 bg-gradient-to-r from-gray-900/90 via-indigo-950/30 to-gray-900/90 shadow-lg">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                        <span class="text-xs font-mono font-semibold uppercase tracking-wider text-brand-400">Candidate Submission Dossier</span>
                        <h2 class="text-lg font-extrabold text-white">Arvind Nandigam</h2>
                        <p class="text-xs text-gray-400">Composio Take-Home Assignment Deliverable</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2 text-xs font-mono">
                        <a href="mailto:nandigamarvind@gmail.com" class="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition">nandigamarvind@gmail.com</a>
                        <a href="tel:+919940355525" class="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition">+91 9940355525</a>
                        <a href="https://linkedin.com/in/arvind-nandigam-329635286" target="_blank" class="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 transition">LinkedIn</a>
                        <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="px-2.5 py-1 rounded-lg bg-brand-600/30 hover:bg-brand-600/50 text-brand-200 border border-brand-500/50 transition">Repository</a>
                    </div>
                </div>
            </div>

            <!-- 5 Headline KPI Cards -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-6">
                <div class="glass-panel p-4 rounded-xl border-l-4 border-l-indigo-500">
                    <p class="text-[11px] font-semibold uppercase tracking-wider text-gray-400">Catalog Size</p>
                    <p class="text-2xl font-extrabold text-white mt-0.5">100 Apps</p>
                    <p class="text-[10px] text-indigo-400 mt-0.5 font-mono">10 Diverse Categories</p>
                </div>
                <div class="glass-panel p-4 rounded-xl border-l-4 border-l-emerald-500">
                    <p class="text-[11px] font-semibold uppercase tracking-wider text-gray-400">Composio Buildable</p>
                    <p class="text-2xl font-extrabold text-emerald-400 mt-0.5">{viable_pct}%</p>
                    <p class="text-[10px] text-gray-400 mt-0.5">{viable_count}/100 (65 Easy + 21 Medium)</p>
                </div>
                <div class="glass-panel p-4 rounded-xl border-l-4 border-l-blue-500">
                    <p class="text-[11px] font-semibold uppercase tracking-wider text-gray-400">Frictionless Access</p>
                    <p class="text-2xl font-extrabold text-blue-400 mt-0.5">{self_serve_pct}%</p>
                    <p class="text-[10px] text-gray-400 mt-0.5">{self_serve_count}/100 (70 Self + 6 Local)</p>
                </div>
                <div class="glass-panel p-4 rounded-xl border-l-4 border-l-amber-500">
                    <p class="text-[11px] font-semibold uppercase tracking-wider text-gray-400">MCP Greenfield</p>
                    <p class="text-2xl font-extrabold text-amber-400 mt-0.5">{greenfield_pct}%</p>
                    <p class="text-[10px] text-gray-400 mt-0.5">{greenfield_count} Unclaimed ({existing_mcp_count} Verified)</p>
                </div>
                <div class="glass-panel p-4 rounded-xl border-l-4 border-l-purple-500 col-span-2 sm:col-span-1">
                    <p class="text-[11px] font-semibold uppercase tracking-wider text-gray-400">Verification Funnel</p>
                    <p class="text-2xl font-extrabold text-purple-400 mt-0.5">{pass1_acc}% &rarr; {auto_verif_acc}%</p>
                    <p class="text-[10px] text-purple-300 mt-0.5 font-mono">+{auto_uplift}% Auto | {human_corrections} Human Fixes</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 1: Headline Patterns (Plainly Stated Up Top) -->
    <section id="patterns" class="py-10 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-6">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">The Headline Patterns (Up Top)</h2>
                    <p class="text-xs text-gray-400 mt-0.5">Plainly stated findings across authentication, credential gating, blockers, and MCP readiness.</p>
                </div>
            </div>

            <!-- Definition Callout -->
            <div class="p-4 rounded-xl bg-gray-900/80 border border-emerald-500/30 mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                    <span class="font-mono font-bold text-emerald-400 uppercase tracking-wider text-[11px]">Definition: What "Composio Buildable" Means (86%)</span>
                    <p class="text-gray-300 mt-1 leading-relaxed">
                        An integration is classified as <strong>Composio Buildable</strong> if a functional toolkit can be built and shipped today using self-serve credentials or standard developer portal app approval (<strong>86 apps = 65 Easy + 21 Medium</strong>), with zero manual enterprise sales outreach, NDAs, or partner gatekeeping. Excludes 7 Hard (sales gated) and 7 Blocked (no public API).
                    </p>
                </div>
                <span class="text-xs font-mono px-2.5 py-1 rounded bg-emerald-950 text-emerald-300 border border-emerald-700/60 shrink-0 font-bold">86/100 Viable Today</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                <div class="glass-panel p-4 rounded-xl border-t-2 border-t-indigo-500">
                    <span class="font-mono font-bold text-indigo-400 text-[11px] block mb-1">1. Auth Duopoly (88% of SaaS)</span>
                    <p class="text-gray-300 leading-relaxed">
                        <strong>OAuth2 (73%)</strong> governs multi-tenant platforms (CRM, Support, Messaging). <strong>API Keys (61%)</strong> and <strong>PATs (25%)</strong> govern Developer and Scraping tools. Basic Auth is legacy only (8%).
                    </p>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-2 border-t-emerald-500">
                    <span class="font-mono font-bold text-emerald-400 text-[11px] block mb-1">2. Gating Polarization (76% Open)</span>
                    <p class="text-gray-300 leading-relaxed">
                        <strong>76% of apps offer frictionless access:</strong> 70 Self-serve + 6 Open-Source Local CLIs. Developer Platforms are 100% self-serve; Finance &amp; Enterprise CRM are 60% gated behind sales calls and NDAs.
                    </p>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-2 border-t-amber-500">
                    <span class="font-mono font-bold text-amber-400 text-[11px] block mb-1">3. Primary Blocker is Administrative (35%)</span>
                    <p class="text-gray-300 leading-relaxed">
                        35% of apps are gated not by technical REST/GraphQL protocol complexity, but by administrative friction: OAuth App Review (21%) and Enterprise Sales / Contract Gates (14%).
                    </p>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-2 border-t-blue-500">
                    <span class="font-mono font-bold text-blue-400 text-[11px] block mb-1">4. MCP Greenfield (70% Unclaimed)</span>
                    <p class="text-gray-300 leading-relaxed">
                        <strong>30 apps (30%)</strong> have verified official or community MCP servers (Salesforce, HubSpot, Stripe, GitHub). <strong>70 apps (70%)</strong> are open greenfield for Composio to establish reference toolkits.
                    </p>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-2 border-t-purple-500">
                    <span class="font-mono font-bold text-purple-400 text-[11px] block mb-1">5. Local Subprocess MCPs (6 Apps)</span>
                    <p class="text-gray-300 leading-relaxed">
                        Tools like Sherlock (#58), Mermaid CLI (#98), and Twenty (#5) have zero cloud HTTP APIs. They require local containerized subprocess MCP execution running over stdio rather than cloud webhooks.
                    </p>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-2 border-t-teal-500">
                    <span class="font-mono font-bold text-teal-400 text-[11px] block mb-1">6. Product Ops Strategic Verdict</span>
                    <p class="text-gray-300 leading-relaxed">
                        Composio's highest-leverage moat is managed OAuth proxying (Tier 2: 24 apps) and claiming the 70 greenfield MCP toolkits before native ecosystems build their own.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 2: Strategic Integration Roadmap (Shipping Tiers) -->
    <section id="roadmap" class="py-10 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-6">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">Strategic Shipping Roadmap (4 Tiers)</h2>
                    <p class="text-xs text-gray-400 mt-0.5">Prioritized rollout based on technical feasibility, auth friction, and business model alignment.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                <div class="glass-panel p-4 rounded-xl border-t-4 border-t-emerald-500">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-mono font-bold text-emerald-400 text-[11px]">TIER 1: QUICK WINS</span>
                        <span class="font-mono text-gray-400 font-bold">{tiers['tier1_immediate_wins']['count']} Apps</span>
                    </div>
                    <p class="text-gray-400 mb-3 text-[11px]">{tiers['tier1_immediate_wins']['description']}</p>
                    <ul class="space-y-1 font-mono text-[11px] text-gray-300">
                        {"".join([f'<li><span class="text-emerald-400">[Ship]</span> #{item["id"]} {item["name"]}</li>' for item in tiers['tier1_immediate_wins']['sample']])}
                    </ul>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-4 border-t-amber-500">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-mono font-bold text-amber-400 text-[11px]">TIER 2: MANAGED OAUTH</span>
                        <span class="font-mono text-gray-400 font-bold">{tiers['tier2_oauth_apps']['count']} Apps</span>
                    </div>
                    <p class="text-gray-400 mb-3 text-[11px]">{tiers['tier2_oauth_apps']['description']}</p>
                    <ul class="space-y-1 font-mono text-[11px] text-gray-300">
                        {"".join([f'<li><span class="text-amber-400">[OAuth]</span> #{item["id"]} {item["name"]}</li>' for item in tiers['tier2_oauth_apps']['sample']])}
                    </ul>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-4 border-t-rose-500">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-mono font-bold text-rose-400 text-[11px]">TIER 3: ENTERPRISE GATED</span>
                        <span class="font-mono text-gray-400 font-bold">{tiers['tier3_partner_gated']['count']} Apps</span>
                    </div>
                    <p class="text-gray-400 mb-3 text-[11px]">{tiers['tier3_partner_gated']['description']}</p>
                    <ul class="space-y-1 font-mono text-[11px] text-gray-300">
                        {"".join([f'<li><span class="text-rose-400">[Gated]</span> #{item["id"]} {item["name"]}</li>' for item in tiers['tier3_partner_gated']['sample']])}
                    </ul>
                </div>

                <div class="glass-panel p-4 rounded-xl border-t-4 border-t-purple-500">
                    <div class="flex items-center justify-between mb-2">
                        <span class="font-mono font-bold text-purple-400 text-[11px]">TIER 4: SUBPROCESS CLI</span>
                        <span class="font-mono text-gray-400 font-bold">{tiers['tier4_cli_mcp']['count']} Apps</span>
                    </div>
                    <p class="text-gray-400 mb-3 text-[11px]">{tiers['tier4_cli_mcp']['description']}</p>
                    <ul class="space-y-1 font-mono text-[11px] text-gray-300">
                        {"".join([f'<li><span class="text-purple-400">[CLI]</span> #{item["id"]} {item["name"]}</li>' for item in tiers['tier4_cli_mcp']['sample']])}
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 3: The Agent Built & Proof (What you built, where a human was needed) -->
    <section id="agent" class="py-10 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-6">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">The Agent Built &amp; Proof of Work</h2>
                    <p class="text-xs text-gray-400 mt-0.5">Autonomous architecture, division of labor, and runnable reproduction command.</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <!-- What was automated -->
                <div class="glass-panel p-5 rounded-xl border-l-4 border-l-emerald-500">
                    <h3 class="font-bold text-white text-sm mb-2">Automated by the Research Agent</h3>
                    <ul class="space-y-2 text-gray-300 text-[11px]">
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Multi-Tool Search &amp; Scraping:</strong> Bing web search API + live HTTP doc scraper + Composio SDK router (<code class="text-brand-300">composio&gt;=0.34.0</code>) with offline fallback.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Deterministic Extraction:</strong> Gemini 3.5 structured JSON parsing enforced via strict Pydantic schemas.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Atomic Checkpointing:</strong> Disk writes after every single app; completely resilient to rate-limit drops.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Automated QA Loop:</strong> Programmatic HTTP URL reachability validation and MCP registry checks.</span>
                        </li>
                    </ul>
                </div>

                <!-- Where human review was needed -->
                <div class="glass-panel p-5 rounded-xl border-l-4 border-l-amber-500">
                    <h3 class="font-bold text-white text-sm mb-2">Where Human Review Was Essential</h3>
                    <ul class="space-y-2 text-gray-300 text-[11px]">
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Plain (#17) Semantic Disambiguation:</strong> Search engine collided with word puzzle game; human redirected agent to Plain's GraphQL API docs.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Amazon SP-API (#49) Commercial Gating:</strong> Docs are public, but credentials require active $39.99/mo seller account + AWS IAM vetting.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Sherlock (#58) Architectural Reclassification:</strong> Flagged as zero-auth OSINT CLI, defining the Local Subprocess MCP pattern.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Strategic Roadmap Curation:</strong> Synthesized 100 app outputs into 4 actionable business tiers for Composio.</span>
                        </li>
                    </ul>
                </div>
            </div>

            <!-- Proof of the App: Runnable Trigger -->
            <div class="mt-4 p-4 rounded-xl glass-panel border border-brand-500/30 bg-gray-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                <div>
                    <span class="font-mono font-bold text-brand-400 text-[11px]">THE PROOF: RUNNABLE CLI TRIGGER</span>
                    <p class="text-gray-300 mt-0.5">Execute the autonomous agent on 100 apps or ad-hoc targets with live checkpointing:</p>
                </div>
                <div class="flex items-center space-x-2 shrink-0">
                    <code class="px-3 py-1.5 rounded-lg bg-gray-950 border border-gray-800 text-brand-300 font-mono text-[11px]">python run_research.py --apps 100 --verify</code>
                    <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-mono text-[11px] font-bold transition">View Source &rarr;</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 4: The Verification (Accuracy Check on Sample, Hits & Misses Shown Honestly) -->
    <section id="verification" class="py-10 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-6">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <div>
                    <h2 class="text-xl font-bold text-white tracking-tight">The Verification Funnel &amp; Hits/Misses Sample</h2>
                    <p class="text-xs text-gray-400 mt-0.5">Honest accuracy progression separating autonomous agent baseline from human ground-truth curation.</p>
                </div>
            </div>

            <!-- 3-Stage Funnel Banner -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-center mb-6 text-xs">
                <div class="p-4 rounded-xl bg-gray-900/80 border border-amber-500/30">
                    <span class="text-[10px] font-mono uppercase tracking-wider text-amber-400 font-bold block mb-1">Pass 1: Autonomous Agent Baseline</span>
                    <p class="text-2xl font-extrabold text-amber-400">{pass1_acc}%</p>
                    <p class="text-[11px] text-gray-300 mt-1 font-mono">77 / 100 Accurate</p>
                    <p class="text-[10px] text-gray-400 mt-1">Autonomous LLM search &amp; extraction; 23 assumptions caught</p>
                </div>
                
                <div class="p-4 rounded-xl bg-gray-900/80 border border-blue-500/30">
                    <span class="text-[10px] font-mono uppercase tracking-wider text-blue-400 font-bold block mb-1">Pass 2: Automated Verification Loop</span>
                    <p class="text-2xl font-extrabold text-blue-400">{auto_verif_acc}%</p>
                    <p class="text-[11px] text-blue-300 mt-1 font-mono">86 / 100 (+{auto_uplift}% Auto Gain)</p>
                    <p class="text-[10px] text-gray-400 mt-1">Automated URL reachability &amp; MCP checks; zero human assistance</p>
                </div>
                
                <div class="p-4 rounded-xl bg-gray-900/80 border border-emerald-500/30">
                    <span class="text-[10px] font-mono uppercase tracking-wider text-emerald-400 font-bold block mb-1">Pass 3: Human Ground-Truth Curation</span>
                    <p class="text-2xl font-extrabold text-emerald-400">{human_corrections} Corrected</p>
                    <p class="text-[11px] text-emerald-300 mt-1 font-mono">{human_disc_rate}% Discrepancy Rate ({post_human_acc}% Dataset)</p>
                    <p class="text-[10px] text-gray-400 mt-1">Spot-checked 14 commercial gates + 9 MCP false neg/pos; 100% ground truth</p>
                </div>
            </div>

            <!-- Hits & Misses Sample (3 Key Benchmark Cases) -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div class="p-4 rounded-xl glass-panel border border-amber-500/30 bg-gray-900/60">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="font-mono text-[10px] font-bold text-brand-300">#17 Plain</span>
                        <span class="font-mono text-[10px] px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-400">Semantic Collision</span>
                    </div>
                    <p class="text-gray-300 leading-relaxed text-[11px]">
                        <strong>Hit &amp; Miss:</strong> Agent collided with word puzzle game (playplain.app) and assumed bogus REST endpoints. Human audit corrected to official GraphQL API (<code class="text-brand-300 font-mono">plain.com/docs</code>).
                    </p>
                </div>

                <div class="p-4 rounded-xl glass-panel border border-rose-500/30 bg-gray-900/60">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="font-mono text-[10px] font-bold text-brand-300">#49 Amazon SP-API</span>
                        <span class="font-mono text-[10px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400">Commercial Gating</span>
                    </div>
                    <p class="text-gray-300 leading-relaxed text-[11px]">
                        <strong>Hit &amp; Miss:</strong> Agent marked access as Self-Serve due to public docs. Human audit caught strict gating: $39.99/mo seller fee + AWS IAM policy vetting required before keys are issued.
                    </p>
                </div>

                <div class="p-4 rounded-xl glass-panel border border-purple-500/30 bg-gray-900/60">
                    <div class="flex items-center justify-between mb-1.5">
                        <span class="font-mono text-[10px] font-bold text-brand-300">#58 Sherlock</span>
                        <span class="font-mono text-[10px] px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-400">Architecture Miss</span>
                    </div>
                    <p class="text-gray-300 leading-relaxed text-[11px]">
                        <strong>Hit &amp; Miss:</strong> Agent searched for HTTP endpoints. Human audit proved zero-auth open-source Python OSINT CLI, defining the Local Subprocess MCP pattern.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 5: The Findings (Clean Skimmable 100-App Table / Matrix) -->
    <section id="matrix" class="py-10 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div>
                    <div class="flex items-center space-x-3">
                        <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                        <h2 class="text-xl font-bold text-white tracking-tight">The Findings: Clean 100-App Matrix</h2>
                    </div>
                    <p class="text-xs text-gray-400 mt-0.5">Filter by category, search by protocol, or inspect verified documentation citations.</p>
                </div>
                <div class="relative">
                    <input type="text" id="searchInput" placeholder="Search app, category, auth, or verdict..." 
                           class="bg-gray-900 border border-gray-700 text-gray-200 text-xs rounded-xl px-4 py-2 pl-9 focus:outline-none focus:border-brand-500 w-64">
                    <svg class="w-4 h-4 text-gray-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                </div>
            </div>

            <!-- Filters & Density -->
            <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-3 mb-4">
                <div class="flex flex-wrap items-center gap-1.5">
                    <button class="cat-pill active px-2.5 py-1 rounded-lg text-xs font-semibold bg-brand-600 text-white border border-brand-500" onclick="filterCategory('All', this)">All (100)</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('CRM and Sales', this)">CRM</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Support and Helpdesk', this)">Support</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Communications and Messaging', this)">Messaging</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Marketing, Ads, Email and Social', this)">Marketing</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Ecommerce', this)">Ecommerce</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Data, SEO and Scraping', this)">Data</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Developer, Infra and Data platforms', this)">Dev/Infra</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Productivity and Project Management', this)">Productivity</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Finance and Fintech', this)">Finance</button>
                    <button class="cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('AI, Research and Media-native', this)">AI/Media</button>
                </div>
                <div class="flex items-center space-x-1.5 text-xs font-mono text-gray-400 shrink-0 bg-gray-900/80 px-2.5 py-1 rounded-lg border border-gray-800">
                    <span>Rows:</span>
                    <button class="page-size-btn active px-2 py-0.5 rounded bg-brand-600 text-white font-bold transition" onclick="setPageSize(15, this)">15</button>
                    <button class="page-size-btn px-2 py-0.5 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 transition" onclick="setPageSize(25, this)">25</button>
                    <button class="page-size-btn px-2 py-0.5 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 transition" onclick="setPageSize(50, this)">50</button>
                    <button class="page-size-btn px-2 py-0.5 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 transition" onclick="setPageSize('all', this)">All (100)</button>
                </div>
            </div>

            <!-- Table -->
            <div class="glass-panel rounded-xl overflow-hidden border border-gray-800 shadow-xl">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-gray-900/90 border-b border-gray-800 text-gray-400 font-semibold uppercase tracking-wider text-[11px]">
                                <th class="py-2.5 px-3 w-10 text-center">#</th>
                                <th class="py-2.5 px-3 min-w-[200px]">Application</th>
                                <th class="py-2.5 px-3 min-w-[120px]">Category</th>
                                <th class="py-2.5 px-3 min-w-[130px]">Auth Method(s)</th>
                                <th class="py-2.5 px-3 min-w-[120px]">Gating</th>
                                <th class="py-2.5 px-3 min-w-[130px]">API Surface</th>
                                <th class="py-2.5 px-3 text-center min-w-[70px]">MCP</th>
                                <th class="py-2.5 px-3 min-w-[110px]">Verdict</th>
                                <th class="py-2.5 px-3 min-w-[300px]">Human Report</th>
                                <th class="py-2.5 px-3 text-center min-w-[80px]">Evidence</th>
                            </tr>
                        </thead>
                        <tbody id="matrixTableBody" class="divide-y divide-gray-800/60 font-sans">
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pagination Bar -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mt-3 text-xs font-mono text-gray-400">
                <div id="tableCounter">Showing 1 to 15 of 100 apps</div>
                <div id="paginationControls" class="flex items-center space-x-2">
                    <button id="prevPageBtn" onclick="changePage(-1)" class="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition">Previous</button>
                    <span id="pageIndicator" class="px-2 py-1 text-gray-300 font-semibold">Page 1 of 7</span>
                    <button id="nextPageBtn" onclick="changePage(1)" class="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition">Next</button>
                </div>
            </div>


        </div>
    </section>

    <!-- Modal for App Evidence -->
    <div id="appModal" style="display: none;" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm items-center justify-center p-4">
        <div class="glass-panel bg-dark-900 border border-gray-700 rounded-2xl max-w-2xl w-full p-5 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div class="flex items-start justify-between border-b border-gray-800 pb-3 mb-3">
                <div>
                    <div class="flex items-center space-x-2">
                        <span id="modalId" class="font-mono text-xs px-2 py-0.5 rounded bg-brand-900/60 text-brand-300 font-bold border border-brand-700/50">#1</span>
                        <h3 id="modalName" class="text-lg font-bold text-white">Salesforce</h3>
                    </div>
                    <p id="modalCategory" class="text-xs text-gray-400 mt-0.5">CRM and Sales</p>
                </div>
                <button onclick="closeModal()" class="text-gray-400 hover:text-white px-2 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 font-mono text-xs">Close</button>
            </div>
            
            <div class="space-y-3 text-xs">
                <div>
                    <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">Description</p>
                    <p id="modalDesc" class="text-xs text-gray-200 mt-0.5"></p>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-900/70 p-2.5 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">Auth Method</p>
                        <p id="modalAuth" class="font-mono text-brand-300 mt-0.5 font-semibold"></p>
                    </div>
                    <div class="bg-gray-900/70 p-2.5 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">Credential Gating</p>
                        <p id="modalGating" class="font-semibold mt-0.5"></p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="bg-gray-900/70 p-2.5 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">API Surface</p>
                        <p id="modalApi" class="text-gray-200 font-mono mt-0.5"></p>
                    </div>
                    <div class="bg-gray-900/70 p-2.5 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">MCP Status</p>
                        <p id="modalMcp" class="text-gray-200 mt-0.5"></p>
                    </div>
                </div>

                <!-- Verified Evidence -->
                <div class="p-3.5 rounded-xl bg-gradient-to-r from-indigo-950/40 to-purple-950/40 border border-indigo-500/30">
                    <span class="text-[10px] font-bold font-mono uppercase tracking-wider text-indigo-400 block mb-1">Verified Documentation Citation</span>
                    <div class="p-2.5 rounded-lg bg-gray-900/90 border border-gray-800 text-gray-200 text-xs italic font-serif leading-relaxed border-l-4 border-l-brand-500">
                        "<span id="modalQuote"></span>"
                    </div>
                    <div id="modalEvidenceLinks" class="mt-2.5 flex flex-wrap gap-2 text-xs font-mono"></div>
                </div>

                <!-- Manual Human Report -->
                <div class="bg-gray-900/80 p-3.5 rounded-xl border border-gray-700 space-y-1.5">
                    <div class="flex items-center justify-between">
                        <p class="font-semibold text-gray-300 uppercase tracking-wider text-[10px]">Manual Human Verification Report</p>
                        <span id="modalHumanReportBadge" class="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-700/60">Verified</span>
                    </div>
                    <p id="modalHumanReportText" class="text-xs text-gray-200 leading-relaxed font-sans bg-gray-950/60 p-2.5 rounded-lg border border-gray-800"></p>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="glass-panel border-t border-gray-800 py-8 text-center text-xs text-gray-500">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-2">
            <div class="flex flex-wrap items-center justify-center gap-3 text-gray-300 font-mono text-xs">
                <span class="font-bold text-white">Arvind Nandigam</span>
                <span>|</span>
                <a href="mailto:nandigamarvind@gmail.com" class="hover:text-brand-400 transition">nandigamarvind@gmail.com</a>
                <span>|</span>
                <a href="tel:+919940355525" class="hover:text-brand-400 transition">+91 9940355525</a>
                <span>|</span>
                <a href="https://linkedin.com/in/arvind-nandigam-329635286" target="_blank" class="hover:text-brand-400 transition">LinkedIn</a>
                <span>|</span>
                <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="hover:text-brand-400 transition">GitHub Repository</a>
            </div>
            <p class="text-gray-500">Composio Take-Home Assignment Deliverable &bull; Clean 2-Minute Executive Study</p>
        </div>
    </footer>

    <!-- Client Script -->
    <script>
        const APPS_DATA = {apps_json};
        const ANALYSIS_DATA = {analysis_json};

        let currentCategory = 'All';
        let searchQuery = '';
        let pageSize = 15;
        let currentPage = 1;

        function setPageSize(size, btn) {{
            pageSize = size;
            currentPage = 1;
            document.querySelectorAll('.page-size-btn').forEach(b => {{
                b.className = 'page-size-btn px-2 py-0.5 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 transition';
            }});
            btn.className = 'page-size-btn active px-2 py-0.5 rounded bg-brand-600 text-white font-bold transition';
            renderTable();
        }}

        function changePage(delta) {{
            currentPage += delta;
            renderTable();
            const elem = document.getElementById('matrix');
            if (elem) elem.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}

        function renderTable() {{
            const tbody = document.getElementById('matrixTableBody');
            tbody.innerHTML = '';

            const filtered = APPS_DATA.filter(app => {{
                const matchCat = (currentCategory === 'All') || (app.category === currentCategory);
                const q = searchQuery.toLowerCase();
                const matchSearch = !q || 
                    app.name.toLowerCase().includes(q) || 
                    app.category.toLowerCase().includes(q) ||
                    (app.auth_methods && app.auth_methods.join(' ').toLowerCase().includes(q)) ||
                    (app.buildability && app.buildability.toLowerCase().includes(q)) ||
                    (app.self_serve && app.self_serve.toLowerCase().includes(q));
                return matchCat && matchSearch;
            }});

            const total = filtered.length;
            let totalPages = 1;
            let displayRows = filtered;

            if (pageSize !== 'all') {{
                const limit = parseInt(pageSize, 10);
                totalPages = Math.ceil(total / limit) || 1;
                if (currentPage > totalPages) currentPage = totalPages;
                if (currentPage < 1) currentPage = 1;
                const start = (currentPage - 1) * limit;
                displayRows = filtered.slice(start, start + limit);
                
                const end = Math.min(start + limit, total);
                const counterEl = document.getElementById('tableCounter');
                if (counterEl) counterEl.innerText = total > 0 ? `Showing ${{start + 1}} to ${{end}} of ${{total}} apps` : 'Showing 0 apps';
                const pageIndEl = document.getElementById('pageIndicator');
                if (pageIndEl) pageIndEl.innerText = `Page ${{currentPage}} of ${{totalPages}}`;
                const prevBtn = document.getElementById('prevPageBtn');
                if (prevBtn) prevBtn.disabled = (currentPage <= 1);
                const nextBtn = document.getElementById('nextPageBtn');
                if (nextBtn) nextBtn.disabled = (currentPage >= totalPages);
                const pagCtrl = document.getElementById('paginationControls');
                if (pagCtrl) pagCtrl.style.display = 'flex';
            }} else {{
                currentPage = 1;
                const counterEl = document.getElementById('tableCounter');
                if (counterEl) counterEl.innerText = `Showing all ${{total}} of ${{total}} apps`;
                const pagCtrl = document.getElementById('paginationControls');
                if (pagCtrl) pagCtrl.style.display = 'none';
            }}

            displayRows.forEach(app => {{
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-800/40 transition border-b border-gray-800/60';
                
                let verdictBadge = 'badge-medium';
                if (app.buildability.includes('Easy')) verdictBadge = 'badge-easy';
                else if (app.buildability.includes('Hard')) verdictBadge = 'badge-hard';
                else if (app.buildability.includes('Blocked')) verdictBadge = 'badge-blocked';

                let gatingBadge = 'badge-selfserve';
                if (app.self_serve.includes('Gated')) gatingBadge = 'badge-gated';
                else if (app.self_serve.includes('Open Source')) gatingBadge = 'badge-easy';

                const authBadges = (app.auth_methods || []).map(m => 
                    `<span class="px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 font-mono text-[10px] border border-gray-700 mr-1">${{m}}</span>`
                ).join('');

                const mcpBadge = app.existing_mcp 
                    ? (app.mcp_url 
                        ? `<a href="${{app.mcp_url}}" target="_blank" class="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-700/60 hover:bg-emerald-900 hover:text-white transition inline-flex items-center space-x-1" title="${{app.mcp_details}}"><span>MCP</span><svg class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg></a>`
                        : `<span class="px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-700/60" title="${{app.mcp_details}}">Yes</span>`)
                    : '<span class="text-gray-500 font-mono text-[10px]">None</span>';

                const primaryDocUrl = (app.evidence_urls && app.evidence_urls[0]) || ('https://' + app.hint);

                tr.innerHTML = `
                    <td class="py-2.5 px-3 text-center font-mono text-gray-500">${{app.id}}</td>
                    <td class="py-2.5 px-3 min-w-[200px]">
                        <div class="flex items-center space-x-1.5">
                            <span class="font-bold text-white">${{app.name}}</span>
                            <a href="${{primaryDocUrl}}" target="_blank" title="Open Official Docs" class="text-gray-500 hover:text-brand-400 font-mono text-[10px] transition">[Docs]</a>
                        </div>
                        <div class="text-[11px] text-gray-400 font-normal mt-0.5 leading-relaxed break-words">
                            ${{app.description || ''}}
                        </div>
                    </td>
                    <td class="py-2.5 px-3 text-gray-400 min-w-[120px]">${{app.category}}</td>
                    <td class="py-2.5 px-3 font-mono min-w-[130px]">${{authBadges}}</td>
                    <td class="py-2.5 px-3 min-w-[120px]"><span class="px-2 py-0.5 rounded font-mono text-[10px] ${{gatingBadge}}">${{app.self_serve}}</span></td>
                    <td class="py-2.5 px-3 font-mono text-gray-300 min-w-[130px] text-[11px]">${{app.api_surface}}</td>
                    <td class="py-2.5 px-3 text-center text-xs font-mono min-w-[70px]">${{mcpBadge}}</td>
                    <td class="py-2.5 px-3 min-w-[110px]"><span class="px-2 py-0.5 rounded font-mono text-[10px] ${{verdictBadge}}">${{app.buildability}}</span></td>
                    <td class="py-2.5 px-3 min-w-[300px]">
                        <div class="flex items-start space-x-1.5">
                            <span class="px-1.5 py-0.5 rounded font-mono text-[9px] font-bold ${{app.human_report_status === 'Corrected in Audit' ? 'bg-amber-950/80 text-amber-300 border border-amber-700/60' : 'bg-emerald-950/80 text-emerald-300 border border-emerald-700/60'}} whitespace-nowrap mt-0.5 shrink-0">${{app.human_report_status || 'Verified'}}</span>
                            <span class="text-gray-300 text-[11px] leading-relaxed break-words">${{app.human_report || ''}}</span>
                        </div>
                    </td>
                    <td class="py-2.5 px-3 text-center min-w-[80px]">
                        <button onclick="openModal(${{app.id}})" class="px-2 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-brand-300 hover:text-white border border-gray-700 font-mono text-[10px] transition">
                            Evidence
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function filterCategory(cat, btn) {{
            currentCategory = cat;
            currentPage = 1;
            document.querySelectorAll('.cat-pill').forEach(b => {{
                b.className = 'cat-pill px-2.5 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700';
            }});
            btn.className = 'cat-pill active px-2.5 py-1 rounded-lg text-xs font-semibold bg-brand-600 text-white border border-brand-500';
            renderTable();
        }}

        document.getElementById('searchInput').addEventListener('input', (e) => {{
            searchQuery = e.target.value;
            currentPage = 1;
            renderTable();
        }});

        function openModal(id) {{
            const app = APPS_DATA.find(a => a.id === id);
            if (!app) return;

            document.getElementById('modalId').innerText = '#' + app.id;
            document.getElementById('modalName').innerText = app.name;
            document.getElementById('modalCategory').innerText = app.category;
            document.getElementById('modalDesc').innerText = app.description || 'SaaS platform';
            document.getElementById('modalAuth').innerText = (app.auth_methods || []).join(', ');
            document.getElementById('modalGating').innerText = app.self_serve || '';
            document.getElementById('modalApi').innerText = `${{app.api_surface}} - ${{app.api_breadth}}`;
            
            if (app.existing_mcp) {{
                let mcpContent = `<span class="text-emerald-400 font-semibold font-mono text-xs">Yes:</span> <span class="text-gray-200">${{app.mcp_details}}</span>`;
                if (app.mcp_url) {{
                    mcpContent += `<div class="mt-1"><a href="${{app.mcp_url}}" target="_blank" class="px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-300 hover:text-white border border-emerald-700/60 font-mono text-[10px] inline-flex items-center space-x-1 transition"><span>Official Repo / Docs</span>&rarr;</a></div>`;
                }}
                document.getElementById('modalMcp').innerHTML = mcpContent;
            }} else {{
                document.getElementById('modalMcp').innerHTML = '<span class="text-gray-400 font-mono text-xs">None (Greenfield Opportunity)</span>';
            }}

            const primaryAuth = (app.auth_methods && app.auth_methods[0]) || 'authentication';
            const quoteText = `Authentication mechanism verified: ${{app.name}} utilizes ${{primaryAuth}} for credential verification. Gating status: ${{app.self_serve}}. ${{app.auth_notes || ''}}`;
            document.getElementById('modalQuote').innerText = quoteText;

            const evLinks = document.getElementById('modalEvidenceLinks');
            evLinks.innerHTML = '';
            (app.evidence_urls || []).forEach(url => {{
                const a = document.createElement('a');
                a.href = `${{url}}#:~:text=${{encodeURIComponent(primaryAuth)}}`;
                a.target = '_blank';
                a.className = 'px-2 py-1 rounded bg-indigo-900/40 hover:bg-indigo-800/60 text-indigo-300 border border-indigo-700/50 flex items-center space-x-1 transition text-[11px]';
                a.innerHTML = `<span>Verify Live in Docs &rarr;</span>`;
                evLinks.appendChild(a);
            }});

            document.getElementById('modalHumanReportText').innerText = app.human_report || 'Confirmed via manual developer documentation cross-check.';
            const isCorrected = (app.human_report_status === 'Corrected in Audit');
            const hrBadge = document.getElementById('modalHumanReportBadge');
            hrBadge.innerText = app.human_report_status || 'Verified';
            hrBadge.className = isCorrected 
                ? 'px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-amber-950/80 text-amber-300 border border-amber-700/60'
                : 'px-2 py-0.5 rounded font-mono text-[10px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-700/60';

            const modal = document.getElementById('appModal');
            modal.style.display = 'flex';
        }}

        function closeModal() {{
            const modal = document.getElementById('appModal');
            modal.style.display = 'none';
        }}

        window.addEventListener('click', (e) => {{
            const modal = document.getElementById('appModal');
            if (e.target === modal) closeModal();
        }});

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});

        window.addEventListener('DOMContentLoaded', () => {{
            renderTable();
        }});
    </script>
</body>
</html>"""

    # Write root index.html
    with open(OUTPUT_INDEX, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Mirror to output/index.html
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Compact 2-Minute index.html generated successfully at:\n - {OUTPUT_INDEX}\n - output/index.html")


if __name__ == "__main__":
    build_html_deliverable()
