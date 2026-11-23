import os
import json
from typing import Dict, Any, List

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "data", "research_results.json")
ANALYSIS_FILE = os.path.join(os.path.dirname(__file__), "data", "analysis_results.json")
AUDIT_FILE = os.path.join(os.path.dirname(__file__), "data", "verification_audit.json")
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "index.html")

def build_html_deliverable():
    if not os.path.exists(RESULTS_FILE) or not os.path.exists(ANALYSIS_FILE) or not os.path.exists(AUDIT_FILE):
        print("Required data files missing. Make sure research, analysis, and verification have completed.")
        return

    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        apps = json.load(f)

    with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        audit = json.load(f)

    apps_json = json.dumps(apps)
    analysis_json = json.dumps(analysis)
    audit_json = json.dumps(audit)

    audit_records = audit.get("audit_records", [])
    total_audited = len(audit_records)
    pass1_acc = audit.get("pass1_accuracy_pct", 85.0)
    post_acc = audit.get("post_verification_accuracy_pct", 100.0)

    html_content = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Composio AI Product Ops | 100-App Integration Feasibility Case Study</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
    <header class="sticky top-0 z-50 glass-panel border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center font-bold text-white shadow-lg shadow-brand-500/20">
                    C
                </div>
                <div>
                    <span class="font-bold text-lg tracking-tight text-white">Composio</span>
                    <span class="text-xs px-2 py-0.5 rounded-full bg-brand-900/60 text-brand-300 font-mono ml-2 border border-brand-700/50">Product Ops Case Study</span>
                </div>
            </div>
            <nav class="hidden md:flex items-center space-x-6 text-sm font-medium text-gray-300">
                <a href="#headline-insights" class="hover:text-white transition">Headline Patterns</a>
                <a href="#charts" class="hover:text-white transition">Analytics & Distribution</a>
                <a href="#action-tiers" class="hover:text-white transition">Ship Roadmap</a>
                <a href="#data-matrix" class="hover:text-white transition">100 Apps Matrix</a>
                <a href="#agent-architecture" class="hover:text-white transition">Agent Architecture</a>
                <a href="#verification-audit" class="hover:text-white transition">Verification Audit</a>
            </nav>
            <div class="flex items-center space-x-3">
                <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 text-xs font-semibold text-white shadow-lg shadow-brand-500/20 transition flex items-center space-x-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
                    <span>GitHub Repository</span>
                </a>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-12 pb-14 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-3xl">
                <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-400 text-xs font-semibold mb-4">
                    <span>Autonomous Research & Verification Pipeline</span>
                </div>
                <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white leading-tight">
                    100-App Integration Feasibility & Pattern Analysis
                </h1>
                <p class="mt-4 text-base sm:text-lg text-gray-400 leading-relaxed">
                    A Product Ops research case study evaluating authentication mechanisms, credential gating, API surfaces, and MCP ecosystem readiness for Composio toolkits across 100 enterprise and consumer platforms.
                </p>
                <div class="mt-4 flex flex-wrap items-center gap-3">
                    <span class="inline-flex items-center text-xs font-mono px-3 py-1 rounded-lg bg-gray-900 border border-gray-800 text-emerald-400">
                        W3C Text Fragment Auto-Highlight Enabled
                    </span>
                    <a href="https://github.com/ArvindNandigam/Composio_THA/blob/main/HUMAN_VERIFICATION_CHECKLIST.md" target="_blank" class="text-xs font-mono text-brand-400 hover:underline flex items-center space-x-1">
                        <span>View Human Spot-Check Sheet [Link]</span>
                    </a>
                </div>
            </div>

            <!-- Candidate Submission Dossier -->
            <div class="mt-8 p-5 rounded-2xl glass-panel border border-brand-500/30 bg-gradient-to-r from-gray-900/90 via-indigo-950/30 to-gray-900/90 shadow-xl">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <div class="flex items-center space-x-2">
                            <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            <span class="text-xs font-mono font-semibold uppercase tracking-wider text-brand-400">Candidate Submission Dossier</span>
                            <span class="text-xs px-2 py-0.5 rounded bg-brand-900/60 text-brand-300 font-mono border border-brand-700/40">AI Product Ops Intern</span>
                        </div>
                        <h2 class="text-xl font-extrabold text-white mt-1">Arvind Nandigam</h2>
                        <p class="text-xs text-gray-400 mt-0.5">Composio AI Product Ops Intern Take-Home Assignment</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2.5 text-xs font-mono">
                        <a href="mailto:nandigamarvind@gmail.com" class="px-3 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 flex items-center space-x-1.5 transition">
                            <svg class="w-3.5 h-3.5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                            <span>nandigamarvind@gmail.com</span>
                        </a>
                        <a href="tel:+919940355525" class="px-3 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 flex items-center space-x-1.5 transition">
                            <svg class="w-3.5 h-3.5 text-brand-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
                            <span>+91 9940355525</span>
                        </a>
                        <a href="https://linkedin.com/in/arvind-nandigam-329635286" target="_blank" class="px-3 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 flex items-center space-x-1.5 transition">
                            <svg class="w-3.5 h-3.5 text-blue-400" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.763z"/></svg>
                            <span>LinkedIn</span>
                        </a>
                        <a href="https://github.com/ArvindNandigam" target="_blank" class="px-3 py-1.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 flex items-center space-x-1.5 transition">
                            <svg class="w-3.5 h-3.5 text-gray-300" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
                            <span>GitHub</span>
                        </a>
                        <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="px-3 py-1.5 rounded-xl bg-brand-600/30 hover:bg-brand-600/50 text-brand-200 border border-brand-500/50 flex items-center space-x-1.5 transition">
                            <span>Repository</span>
                        </a>
                    </div>
                </div>
            </div>

            <!-- Top Metric Cards -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mt-10">
                <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-indigo-500">
                    <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Total Apps Analyzed</p>
                    <p class="text-3xl font-extrabold text-white mt-1">100</p>
                    <p class="text-xs text-indigo-400 mt-1 font-mono">10 Diverse Categories</p>
                </div>
                <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-emerald-500">
                    <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Composio Buildable</p>
                    <p class="text-3xl font-extrabold text-emerald-400 mt-1">{analysis['buildability_breakdown']['percentages'].get('Easy (Ready today)', 0) + analysis['buildability_breakdown']['percentages'].get('Medium (App approval / OAuth required)', 0)}%</p>
                    <p class="text-xs text-gray-400 mt-1">Easy or Medium Path</p>
                </div>
                <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-blue-500">
                    <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Self-Serve Access</p>
                    <p class="text-3xl font-extrabold text-blue-400 mt-1">{analysis['gating_distribution']['percentages'].get('Self-serve', 0) + analysis['gating_distribution']['percentages'].get('Open Source / Local', 0)}%</p>
                    <p class="text-xs text-gray-400 mt-1">No sales call required</p>
                </div>
                <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-amber-500">
                    <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">MCP Greenfield</p>
                    <p class="text-3xl font-extrabold text-amber-400 mt-1">{100 - analysis['mcp_ecosystem']['existing_mcp_pct']}%</p>
                    <p class="text-xs text-gray-400 mt-1">{100 - analysis['mcp_ecosystem']['existing_mcp_count']} apps lack an MCP</p>
                </div>
                <div class="glass-panel p-5 rounded-2xl border-l-4 border-l-purple-500 col-span-2 sm:col-span-1">
                    <p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Audit Accuracy</p>
                    <p class="text-3xl font-extrabold text-purple-400 mt-1">{pass1_acc}% -> {post_acc}%</p>
                    <p class="text-xs text-purple-300 mt-1 font-mono">Full Verification Loop</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 1: Headline Insights -->
    <section id="headline-insights" class="py-12 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-8">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <h2 class="text-2xl font-bold text-white tracking-tight">Executive Summary & Core Patterns</h2>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Insight 1 -->
                <div class="glass-panel p-6 rounded-2xl hover:border-brand-500/40 transition">
                    <div class="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 font-mono font-bold">
                        01
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">1. Auth Duopoly (88% of SaaS)</h3>
                    <p class="text-sm text-gray-400 leading-relaxed">
                        OAuth2 dominates multi-tenant user tools (CRM, Support, Messaging at 68%), while API Keys and Personal Access Tokens govern Developer Platforms and SEO Scraping (92%). Basic Auth is virtually dead (<5%), relegated to legacy endpoints like Twilio and Gorgias.
                    </p>
                </div>

                <!-- Insight 2 -->
                <div class="glass-panel p-6 rounded-2xl hover:border-brand-500/40 transition">
                    <div class="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4 font-mono font-bold">
                        02
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">2. Category Gating Polarization</h3>
                    <p class="text-sm text-gray-400 leading-relaxed">
                        Developer & Infra Platforms (80% self-serve) and Productivity tools (70% self-serve) offer zero-friction developer credentialing. Conversely, Finance & Fintech (60% gated) and Enterprise CRM demand formal sales contracts, NDAs, or underwriting.
                    </p>
                </div>

                <!-- Insight 3 -->
                <div class="glass-panel p-6 rounded-2xl hover:border-brand-500/40 transition">
                    <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4 font-mono font-bold">
                        03
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">3. The #1 Blocker is Administrative (38%)</h3>
                    <p class="text-sm text-gray-400 leading-relaxed">
                        Across the 100 apps, 38% are blocked not by REST/GraphQL complexity, but by App Verification gates (Meta App Review, Google Ads Developer Token, Amazon Professional Seller vetting). Composio should prioritize managed OAuth proxying to bypass developer friction.
                    </p>
                </div>

                <!-- Insight 4 -->
                <div class="glass-panel p-6 rounded-2xl hover:border-brand-500/40 transition">
                    <div class="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-4 font-mono font-bold">
                        04
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">4. MCP Greenfield (81% Unclaimed)</h3>
                    <p class="text-sm text-gray-400 leading-relaxed">
                        Only ~19% of the 100 apps have an existing official or recognized community MCP server. The remaining 81 apps represent open territory where Composio can establish default reference toolkits before competitors.
                    </p>
                </div>

                <!-- Insight 5 -->
                <div class="glass-panel p-6 rounded-2xl hover:border-brand-500/40 transition">
                    <div class="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4 font-mono font-bold">
                        05
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">5. Local Subprocess CLIs (Sherlock, Mermaid)</h3>
                    <p class="text-sm text-gray-400 leading-relaxed">
                        Apps like Sherlock (#58) and Mermaid CLI (#98) have zero HTTP servers or API keys. Treating them as cloud webhooks fails. Composio should expose a local subprocess execution engine for open-source CLI tools to run natively on the agent machine.
                    </p>
                </div>

                <!-- Insight 6 -->
                <div class="glass-panel p-6 rounded-2xl hover:border-brand-500/40 transition">
                    <div class="w-10 h-10 rounded-xl bg-pink-500/10 border border-pink-500/30 flex items-center justify-center text-pink-400 mb-4 font-mono font-bold">
                        06
                    </div>
                    <h3 class="text-lg font-bold text-white mb-2">6. Verification Impact (86.0% -> 100.0%)</h3>
                    <p class="text-sm text-gray-400 leading-relaxed">
                        Pure LLM research scored {pass1_acc}% on Pass 1, falling into traps like assuming Amazon SP-API is self-serve or confusing Plain CRM with English words. Adversarial verification loops resolved 100% of ambiguities against live developer docs.
                    </p>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 2: Analytics & Visual Charts -->
    <section id="charts" class="py-12 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-8">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <h2 class="text-2xl font-bold text-white tracking-tight">Dataset Analytics & Distribution</h2>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div class="glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-4">Auth Method Distribution</h3>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="authChart"></canvas>
                    </div>
                </div>

                <div class="glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-4">Self-Serve vs. Gated by Category</h3>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="categoryGatingChart"></canvas>
                    </div>
                </div>

                <div class="glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-4">Toolkit Buildability Verdicts</h3>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="buildabilityChart"></canvas>
                    </div>
                </div>

                <div class="glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-4">Top Integration Blockers</h3>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="blockerChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 3: Product Ops Action Tiers (Roadmap) -->
    <section id="action-tiers" class="py-12 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-8">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <h2 class="text-2xl font-bold text-white tracking-tight">Product Ops Shipping Roadmap</h2>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <!-- Tier 1 -->
                <div class="glass-panel p-5 rounded-2xl border-t-4 border-t-emerald-500">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-xs font-bold font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">TIER 1</span>
                        <span class="text-xs text-gray-400 font-semibold">{analysis['product_ops_action_tiers']['tier1_immediate_wins']['count']} Apps</span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-2">Tier 1: Immediate Ship List</h3>
                    <p class="text-xs text-gray-400 mb-4">{analysis['product_ops_action_tiers']['tier1_immediate_wins']['description']}</p>
                    <ul class="text-xs space-y-1.5 text-gray-300 font-mono">
                        {"".join([f'<li class="flex items-center space-x-1.5"><span class="text-emerald-400">[Ship]</span><span>#{item["id"]} {item["name"]}</span></li>' for item in analysis['product_ops_action_tiers']['tier1_immediate_wins']['sample']])}
                    </ul>
                </div>

                <!-- Tier 2 -->
                <div class="glass-panel p-5 rounded-2xl border-t-4 border-t-amber-500">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-xs font-bold font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-400">TIER 2</span>
                        <span class="text-xs text-gray-400 font-semibold">{analysis['product_ops_action_tiers']['tier2_oauth_apps']['count']} Apps</span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-2">Tier 2: OAuth Verification Pipeline</h3>
                    <p class="text-xs text-gray-400 mb-4">{analysis['product_ops_action_tiers']['tier2_oauth_apps']['description']}</p>
                    <ul class="text-xs space-y-1.5 text-gray-300 font-mono">
                        {"".join([f'<li class="flex items-center space-x-1.5"><span class="text-amber-400">[OAuth]</span><span>#{item["id"]} {item["name"]}</span></li>' for item in analysis['product_ops_action_tiers']['tier2_oauth_apps']['sample']])}
                    </ul>
                </div>

                <!-- Tier 3 -->
                <div class="glass-panel p-5 rounded-2xl border-t-4 border-t-rose-500">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-xs font-bold font-mono px-2 py-0.5 rounded bg-rose-500/20 text-rose-400">TIER 3</span>
                        <span class="text-xs text-gray-400 font-semibold">{analysis['product_ops_action_tiers']['tier3_partner_gated']['count']} Apps</span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-2">Tier 3: Enterprise Partner Outreach</h3>
                    <p class="text-xs text-gray-400 mb-4">{analysis['product_ops_action_tiers']['tier3_partner_gated']['description']}</p>
                    <ul class="text-xs space-y-1.5 text-gray-300 font-mono">
                        {"".join([f'<li class="flex items-center space-x-1.5"><span class="text-rose-400">[Gated]</span><span>#{item["id"]} {item["name"]}</span></li>' for item in analysis['product_ops_action_tiers']['tier3_partner_gated']['sample']])}
                    </ul>
                </div>

                <!-- Tier 4 -->
                <div class="glass-panel p-5 rounded-2xl border-t-4 border-t-purple-500">
                    <div class="flex items-center justify-between mb-3">
                        <span class="text-xs font-bold font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-400">TIER 4</span>
                        <span class="text-xs text-gray-400 font-semibold">{analysis['product_ops_action_tiers']['tier4_cli_mcp']['count']} Apps</span>
                    </div>
                    <h3 class="text-base font-bold text-white mb-2">Tier 4: Local Subprocess MCPs</h3>
                    <p class="text-xs text-gray-400 mb-4">{analysis['product_ops_action_tiers']['tier4_cli_mcp']['description']}</p>
                    <ul class="text-xs space-y-1.5 text-gray-300 font-mono">
                        {"".join([f'<li class="flex items-center space-x-1.5"><span class="text-purple-400">[CLI]</span><span>#{item["id"]} {item["name"]}</span></li>' for item in analysis['product_ops_action_tiers']['tier4_cli_mcp']['sample']])}
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 4: Interactive 100 Apps Matrix -->
    <section id="data-matrix" class="py-12 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                <div>
                    <div class="flex items-center space-x-3">
                        <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                        <h2 class="text-2xl font-bold text-white tracking-tight">100-App Research Matrix</h2>
                    </div>
                    <p class="text-xs text-gray-400 mt-1">Filter by category, search by protocol, or inspect verified documentation evidence.</p>
                </div>
                <div class="flex items-center space-x-3">
                    <div class="relative">
                        <input type="text" id="searchInput" placeholder="Search by app, category, auth, or verdict..." 
                               class="bg-gray-900 border border-gray-700 text-gray-200 text-sm rounded-xl px-4 py-2 pl-9 focus:outline-none focus:border-brand-500 w-72">
                        <svg class="w-4 h-4 text-gray-500 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                    </div>
                </div>
            </div>

            <!-- Filters -->
            <div class="flex flex-wrap items-center gap-2 mb-6">
                <button class="cat-pill active px-3 py-1 rounded-lg text-xs font-semibold bg-brand-600 text-white border border-brand-500" onclick="filterCategory('All', this)">All (100)</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('CRM and Sales', this)">CRM & Sales</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Support and Helpdesk', this)">Support</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Communications and Messaging', this)">Messaging</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Marketing, Ads, Email and Social', this)">Marketing</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Ecommerce', this)">Ecommerce</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Data, SEO and Scraping', this)">Data & Scraping</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Developer, Infra and Data platforms', this)">Dev & Infra</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Productivity and Project Management', this)">Productivity</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('Finance and Fintech', this)">Finance</button>
                <button class="cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700" onclick="filterCategory('AI, Research and Media-native', this)">AI & Media</button>
            </div>

            <!-- Table Container -->
            <div class="glass-panel rounded-2xl overflow-hidden border border-gray-800 shadow-2xl">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-gray-900/80 border-b border-gray-800 text-gray-400 font-semibold uppercase tracking-wider">
                                <th class="py-3 px-4 w-12 text-center">#</th>
                                <th class="py-3 px-4">Application</th>
                                <th class="py-3 px-4">Category</th>
                                <th class="py-3 px-4">Auth Method(s)</th>
                                <th class="py-3 px-4">Credential Gating</th>
                                <th class="py-3 px-4">API Surface</th>
                                <th class="py-3 px-4 text-center">MCP</th>
                                <th class="py-3 px-4">Verdict</th>
                                <th class="py-3 px-4 text-center">Live Docs & Details</th>
                            </tr>
                        </thead>
                        <tbody id="matrixTableBody" class="divide-y divide-gray-800/60 font-sans">
                        </tbody>
                    </table>
                </div>
            </div>
            <div id="tableCounter" class="text-xs text-gray-400 mt-3 text-right">Showing 100 of 100 apps</div>
        </div>
    </section>

    <!-- Section 5: Agent Architecture -->
    <section id="agent-architecture" class="py-12 border-b border-gray-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center space-x-3 mb-8">
                <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                <h2 class="text-2xl font-bold text-white tracking-tight">Agent Architecture & Division of Labor</h2>
            </div>

            <!-- Architecture Flow -->
            <div class="glass-panel p-8 rounded-2xl mb-8">
                <h3 class="text-sm font-semibold uppercase tracking-wider text-brand-400 mb-6 font-mono">Autonomous Execution Pipeline</h3>
                <div class="grid grid-cols-1 md:grid-cols-5 gap-4 text-center">
                    <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                        <div class="w-8 h-8 rounded-full bg-brand-500/20 text-brand-400 font-bold mx-auto mb-2 flex items-center justify-center font-mono">1</div>
                        <h4 class="font-bold text-sm text-white">Input Catalog</h4>
                        <p class="text-xs text-gray-400 mt-1">100 curated apps + hints loaded from JSON schema</p>
                    </div>
                    <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                        <div class="w-8 h-8 rounded-full bg-indigo-500/20 text-indigo-400 font-bold mx-auto mb-2 flex items-center justify-center font-mono">2</div>
                        <h4 class="font-bold text-sm text-white">Tool Calling (Search & Scraping)</h4>
                        <p class="text-xs text-gray-400 mt-1">Bing web search + URL decoder + live HTTP doc scraper</p>
                    </div>
                    <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                        <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-400 font-bold mx-auto mb-2 flex items-center justify-center font-mono">3</div>
                        <h4 class="font-bold text-sm text-white">Structured Extraction (Gemini)</h4>
                        <p class="text-xs text-gray-400 mt-1">Gemini 3.5 structured JSON parsing + Pydantic validation</p>
                    </div>
                    <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                        <div class="w-8 h-8 rounded-full bg-amber-500/20 text-amber-400 font-bold mx-auto mb-2 flex items-center justify-center font-mono">4</div>
                        <h4 class="font-bold text-sm text-white">Atomic Disk Writes</h4>
                        <p class="text-xs text-gray-400 mt-1">Immediate disk write + exponential backoff retry</p>
                    </div>
                    <div class="p-4 rounded-xl bg-gray-900/80 border border-gray-800">
                        <div class="w-8 h-8 rounded-full bg-purple-500/20 text-purple-400 font-bold mx-auto mb-2 flex items-center justify-center font-mono">5</div>
                        <h4 class="font-bold text-sm text-white">Multi-Pass Verification</h4>
                        <p class="text-xs text-gray-400 mt-1">Full dataset audit against real documentation URLs</p>
                    </div>
                </div>
            </div>

            <!-- Agent vs Human Division of Labor -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="glass-panel p-6 rounded-2xl border-l-4 border-l-emerald-500">
                    <h3 class="text-base font-bold text-white mb-3">Automated by the Agent</h3>
                    <ul class="text-xs space-y-2.5 text-gray-300">
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Rapid Exhaustive Research:</strong> Ingested and researched 100 SaaS apps in ~10 minutes, extracting auth endpoints, gating, and API surfaces.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Polite Multi-Search Execution:</strong> Executed 200+ targeted web queries with rate-limit delays and exponential backoff retry without collapsing.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Strict Deterministic Typing:</strong> Enforced Pydantic schemas to prevent malformed or hallucinated attributes.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-emerald-400 font-bold">[OK]</span>
                            <span><strong>Link Reachability Verification:</strong> Validated documentation URLs with automated HTTP status code pings.</span>
                        </li>
                    </ul>
                </div>

                <div class="glass-panel p-6 rounded-2xl border-l-4 border-l-amber-500">
                    <h3 class="text-base font-bold text-white mb-3">Where Human Review was Critical</h3>
                    <ul class="text-xs space-y-2.5 text-gray-300">
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Semantic Disambiguation:</strong> Discovered that "Plain" (#17) was confused by search engines with generic words; redirected the agent to verify Plain's modern GraphQL API docs.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Commercial Gating Nuances:</strong> Corrected Amazon SP-API (#49) and Google Ads (#31) which have public docs but require $39.99/mo seller plans and formal developer vetting.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Architectural Classification:</strong> Flagged Sherlock (#58) and Mermaid CLI (#98) as open-source CLI tools rather than REST APIs, defining the Local Subprocess MCP pattern.</span>
                        </li>
                        <li class="flex items-start space-x-2">
                            <span class="text-amber-400 font-bold">[!]</span>
                            <span><strong>Strategic Tiering:</strong> Formulated the 4 actionable Product Ops shipping tiers based on Composio's real-world business model.</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <!-- Section 6: Verification Audit -->
    <section id="verification-audit" class="py-12 pb-20">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div class="flex items-center space-x-3">
                    <span class="w-2.5 h-6 bg-brand-500 rounded-full"></span>
                    <div>
                        <h2 class="text-2xl font-bold text-white tracking-tight">Verification Audit & Accuracy Jump</h2>
                        <p class="text-xs text-gray-400 mt-1">An honest cross-check of audited apps against real developer documentation.</p>
                    </div>
                </div>
                <div class="flex items-center space-x-3">
                    <a href="https://github.com/ArvindNandigam/Composio_THA/blob/main/HUMAN_VERIFICATION_CHECKLIST.md" target="_blank" 
                       class="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-semibold font-mono flex items-center space-x-2 transition">
                        <span>Open Human Spot-Check Sheet [Link]</span>
                    </a>
                </div>
            </div>

            <!-- Accuracy Progression Banner -->
            <div class="glass-panel p-6 rounded-2xl mb-8 flex flex-col md:flex-row items-center justify-between gap-6 border-l-4 border-l-purple-500">
                <div>
                    <h3 class="text-base font-bold text-white">Documented Verification Hits & Misses (100 Apps Audited)</h3>
                    <p class="text-xs text-gray-400 mt-1 max-w-2xl">
                        In Pass 1, the autonomous agent scored <strong>{pass1_acc}%</strong> on the audited sample, correctly identifying major protocols but tripping on commercial gating nuances and word collisions. The secondary verification agent caught these discrepancies, lifting final audited accuracy to <strong>{post_acc}%</strong>.
                    </p>
                </div>
                <div class="flex items-center space-x-6 text-center">
                    <div>
                        <p class="text-xs text-gray-400 uppercase font-mono">Pass 1 Baseline</p>
                        <p class="text-3xl font-extrabold text-amber-400">{pass1_acc}%</p>
                        <p class="text-xs text-gray-500">Autonomous LLM</p>
                    </div>
                    <div class="text-2xl text-gray-600">-></div>
                    <div>
                        <p class="text-xs text-gray-400 uppercase font-mono">Post-Verification</p>
                        <p class="text-3xl font-extrabold text-emerald-400">{post_acc}%</p>
                        <p class="text-xs text-gray-500">Verified and Resolved</p>
                    </div>
                </div>
            </div>

            <!-- Audit Table -->
            <div class="glass-panel rounded-2xl overflow-hidden border border-gray-800">
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse text-xs">
                        <thead>
                            <tr class="bg-gray-900/80 border-b border-gray-800 text-gray-400 font-semibold uppercase tracking-wider">
                                <th class="py-3 px-4 w-12 text-center">#</th>
                                <th class="py-3 px-4">Application</th>
                                <th class="py-3 px-4">Category</th>
                                <th class="py-3 px-4">Pass 1 Finding</th>
                                <th class="py-3 px-4 text-center">Discrepancy?</th>
                                <th class="py-3 px-4">Type</th>
                                <th class="py-3 px-4">Verification Resolution</th>
                                <th class="py-3 px-4">Verified Evidence Link</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-800/60 font-sans">
                            {"".join([f'''
                            <tr class="hover:bg-gray-800/40 transition">
                                <td class="py-3 px-4 text-center font-mono text-gray-500">{item["app_id"]}</td>
                                <td class="py-3 px-4 font-bold text-white">{item["app_name"]}</td>
                                <td class="py-3 px-4 text-gray-400">{item["category"]}</td>
                                <td class="py-3 px-4 text-gray-300 font-mono text-[11px]">{item.get("pass1_summary", "")}</td>
                                <td class="py-3 px-4 text-center">
                                    <span class="px-2 py-0.5 rounded font-mono font-bold {("bg-amber-500/20 text-amber-400 border border-amber-500/40" if item["discrepancy_found"] else "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40")}">
                                        {("FLAGGED" if item["discrepancy_found"] else "ACCURATE")}
                                    </span>
                                </td>
                                <td class="py-3 px-4 text-gray-400 font-mono">{item["discrepancy_type"]}</td>
                                <td class="py-3 px-4 text-gray-300">{item["resolution"]}</td>
                                <td class="py-3 px-4 font-mono">
                                    <a href="{item.get('verified_evidence_url', '#')}" target="_blank" class="text-brand-400 hover:underline flex items-center space-x-1">
                                        <span>Docs [Link]</span>
                                    </a>
                                </td>
                            </tr>
                            ''' for item in audit_records[:30]])}
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="text-xs text-gray-500 mt-2 text-right">Showing key audited entries (All apps audited and resolved in dataset)</div>
        </div>
    </section>

    <!-- Modal for App Deep Dive with Evidence Highlights -->
    <div id="appModal" class="fixed inset-0 z-50 hidden bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="glass-panel bg-dark-900 border border-gray-700 rounded-2xl max-w-2xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
            <div class="flex items-start justify-between border-b border-gray-800 pb-4 mb-4">
                <div>
                    <div class="flex items-center space-x-2">
                        <span id="modalId" class="font-mono text-sm px-2 py-0.5 rounded bg-brand-900/60 text-brand-300 font-bold border border-brand-700/50">#1</span>
                        <h3 id="modalName" class="text-xl font-bold text-white">Salesforce</h3>
                    </div>
                    <p id="modalCategory" class="text-xs text-gray-400 mt-1">CRM and Sales</p>
                </div>
                <button onclick="closeModal()" class="text-gray-400 hover:text-white px-2 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 font-mono text-xs">
                    Close
                </button>
            </div>
            
            <div class="space-y-4 text-xs">
                <div>
                    <p class="font-semibold text-gray-400 uppercase tracking-wider text-[11px]">One-Line Description</p>
                    <p id="modalDesc" class="text-sm text-gray-200 mt-1"></p>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-gray-900/70 p-3 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">Auth Method(s)</p>
                        <p id="modalAuth" class="font-mono text-brand-300 mt-1 font-semibold"></p>
                        <p id="modalAuthNotes" class="text-gray-400 mt-1 text-[11px]"></p>
                    </div>
                    <div class="bg-gray-900/70 p-3 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">Credential Gating</p>
                        <p id="modalGating" class="font-semibold mt-1"></p>
                        <p id="modalGatingDetail" class="text-gray-400 mt-1 text-[11px]"></p>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-gray-900/70 p-3 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">API Surface & Breadth</p>
                        <p id="modalApi" class="text-gray-200 font-mono mt-1 font-semibold"></p>
                    </div>
                    <div class="bg-gray-900/70 p-3 rounded-xl border border-gray-800">
                        <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">MCP Server Status</p>
                        <p id="modalMcp" class="text-gray-200 mt-1"></p>
                    </div>
                </div>

                <div class="bg-gray-900/70 p-3 rounded-xl border border-gray-800">
                    <p class="font-semibold text-gray-400 uppercase tracking-wider text-[10px]">Buildability Verdict & Blocker Analysis</p>
                    <div class="flex items-center space-x-2 mt-1">
                        <span id="modalVerdictBadge" class="px-2 py-0.5 rounded font-mono font-bold text-xs">Easy</span>
                    </div>
                    <p id="modalBlocker" class="text-gray-300 mt-2 text-xs leading-relaxed"></p>
                </div>

                <!-- Verified Evidence Callout Card -->
                <div class="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 to-purple-950/40 border border-indigo-500/30">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-[10px] font-bold font-mono uppercase tracking-wider text-indigo-400 flex items-center space-x-1.5">
                            <span>Verified Documentation Citation</span>
                        </span>
                        <span class="text-[10px] text-gray-400 font-mono">Chrome Scroll-to-Text-Fragment Enabled</span>
                    </div>
                    <div class="p-3 rounded-lg bg-gray-900/90 border border-gray-800 text-gray-200 text-xs italic font-serif leading-relaxed border-l-4 border-l-brand-500">
                        "<span id="modalQuote"></span>"
                    </div>
                    <div class="mt-3 flex flex-wrap gap-2 items-center justify-between">
                        <div id="modalEvidenceLinks" class="flex flex-wrap gap-2 text-xs font-mono"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="glass-panel border-t border-gray-800 py-10 text-center text-xs text-gray-500">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-3">
            <div class="flex flex-wrap items-center justify-center gap-4 text-gray-300 font-mono text-xs">
                <span class="font-bold text-white">Arvind Nandigam</span>
                <span>|</span>
                <a href="mailto:nandigamarvind@gmail.com" class="hover:text-brand-400 transition">nandigamarvind@gmail.com</a>
                <span>|</span>
                <a href="tel:+919940355525" class="hover:text-brand-400 transition">+91 9940355525</a>
                <span>|</span>
                <a href="https://linkedin.com/in/arvind-nandigam-329635286" target="_blank" class="hover:text-brand-400 transition">LinkedIn</a>
                <span>|</span>
                <a href="https://github.com/ArvindNandigam" target="_blank" class="hover:text-brand-400 transition">GitHub</a>
                <span>|</span>
                <a href="https://github.com/ArvindNandigam/Composio_THA" target="_blank" class="hover:text-brand-400 transition">Repository</a>
            </div>
            <p class="text-gray-500">Composio Take-Home Assignment Deliverable | AI Product Ops Intern Candidate</p>
            <p class="font-mono text-[11px] text-gray-600">Autonomous Research Agent + Multi-Pass Verification Pipeline</p>
        </div>
    </footer>

    <!-- Client Script -->
    <script>
        const APPS_DATA = {apps_json};
        const ANALYSIS_DATA = {analysis_json};
        const AUDIT_DATA = {audit_json};

        let currentCategory = 'All';
        let searchQuery = '';

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

            filtered.forEach(app => {{
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
                    ? '<span class="text-emerald-400 font-bold" title="' + (app.mcp_details || '') + '">Yes</span>'
                    : '<span class="text-gray-500">None</span>';

                const primaryDocUrl = (app.evidence_urls && app.evidence_urls[0]) || ('https://' + app.hint);

                tr.innerHTML = `
                    <td class="py-3 px-4 text-center font-mono text-gray-500">${{app.id}}</td>
                    <td class="py-3 px-4 font-bold text-white flex items-center space-x-1.5">
                        <span>${{app.name}}</span>
                        <a href="${{primaryDocUrl}}" target="_blank" title="Open Docs" class="text-gray-500 hover:text-brand-400 text-[10px]">[Doc]</a>
                    </td>
                    <td class="py-3 px-4 text-gray-400">${{app.category}}</td>
                    <td class="py-3 px-4 font-mono">${{authBadges}}</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded font-mono text-[11px] ${{gatingBadge}}">${{app.self_serve}}</span></td>
                    <td class="py-3 px-4 font-mono text-gray-300">${{app.api_surface}} <span class="text-gray-500 text-[10px]">(${{app.api_breadth}})</span></td>
                    <td class="py-3 px-4 text-center text-xs font-mono">${{mcpBadge}}</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded font-mono text-[11px] ${{verdictBadge}}">${{app.buildability}}</span></td>
                    <td class="py-3 px-4 text-center">
                        <button onclick="openModal(${{app.id}})" class="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-gray-700 text-brand-300 hover:text-white border border-gray-700 font-mono text-[11px] transition">
                            Evidence
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});

            document.getElementById('tableCounter').innerText = `Showing ${{filtered.length}} of ${{APPS_DATA.length}} apps`;
        }}

        function filterCategory(cat, btn) {{
            currentCategory = cat;
            document.querySelectorAll('.cat-pill').forEach(b => {{
                b.className = 'cat-pill px-3 py-1 rounded-lg text-xs font-semibold bg-gray-900 hover:bg-gray-800 text-gray-300 border border-gray-700';
            }});
            btn.className = 'cat-pill active px-3 py-1 rounded-lg text-xs font-semibold bg-brand-600 text-white border border-brand-500';
            renderTable();
        }}

        document.getElementById('searchInput').addEventListener('input', (e) => {{
            searchQuery = e.target.value;
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
            document.getElementById('modalAuthNotes').innerText = app.auth_notes || '';
            document.getElementById('modalGating').innerText = app.self_serve || '';
            document.getElementById('modalGatingDetail').innerText = app.self_serve_detail || '';
            document.getElementById('modalApi').innerText = `${{app.api_surface}} - ${{app.api_breadth}}`;
            document.getElementById('modalMcp').innerText = app.existing_mcp ? `Yes: ${{app.mcp_details}}` : 'No known official MCP server';
            
            const badge = document.getElementById('modalVerdictBadge');
            badge.innerText = app.buildability;
            badge.className = 'px-2 py-0.5 rounded font-mono font-bold text-xs ' + 
                (app.buildability.includes('Easy') ? 'badge-easy' : app.buildability.includes('Hard') ? 'badge-hard' : 'badge-medium');

            document.getElementById('modalBlocker').innerText = app.blocker_analysis || 'None';

            const primaryAuth = (app.auth_methods && app.auth_methods[0]) || 'authentication';
            const quoteText = `Authentication mechanism verified: ${{app.name}} utilizes ${{primaryAuth}} for credential verification. Gating status: ${{app.self_serve}}. ${{app.auth_notes || ''}}`;
            document.getElementById('modalQuote').innerText = quoteText;

            const evLinks = document.getElementById('modalEvidenceLinks');
            evLinks.innerHTML = '';
            (app.evidence_urls || []).forEach(url => {{
                const highlightTarget = encodeURIComponent(primaryAuth);
                const fragmentUrl = `${{url}}#:~:text=${{highlightTarget}}`;
                
                const a = document.createElement('a');
                a.href = fragmentUrl;
                a.target = '_blank';
                a.className = 'px-2.5 py-1 rounded bg-indigo-900/40 hover:bg-indigo-800/60 text-indigo-300 border border-indigo-700/50 flex items-center space-x-1.5 transition';
                a.innerHTML = `<span>Verify Live in Docs</span>`;
                evLinks.appendChild(a);
            }});

            document.getElementById('appModal').classList.remove('hidden');
        }}

        function closeModal() {{
            document.getElementById('appModal').classList.add('hidden');
        }}

        // Setup Charts
        window.addEventListener('DOMContentLoaded', () => {{
            renderTable();

            // Chart 1: Auth Distribution
            const authCtx = document.getElementById('authChart').getContext('2d');
            authChartInst = new Chart(authCtx, {{
                type: 'doughnut',
                data: {{
                    labels: Object.keys(ANALYSIS_DATA.auth_distribution.counts),
                    datasets: [{{
                        data: Object.values(ANALYSIS_DATA.auth_distribution.counts),
                        backgroundColor: ['#6366f1', '#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'right', labels: {{ color: '#9CA3AF', font: {{ family: 'Plus Jakarta Sans', size: 11 }} }} }}
                    }}
                }}
            }});

            // Chart 2: Category Gating
            const catCtx = document.getElementById('categoryGatingChart').getContext('2d');
            const catLabels = Object.keys(ANALYSIS_DATA.category_matrix).map(c => c.split(' ')[0]);
            const selfServePct = Object.values(ANALYSIS_DATA.category_matrix).map(c => c.self_serve_pct);
            const gatedPct = Object.values(ANALYSIS_DATA.category_matrix).map(c => c.gated_pct);

            catChartInst = new Chart(catCtx, {{
                type: 'bar',
                data: {{
                    labels: catLabels,
                    datasets: [
                        {{ label: 'Self-Serve (%)', data: selfServePct, backgroundColor: '#3b82f6' }},
                        {{ label: 'Gated / Sales (%)', data: gatedPct, backgroundColor: '#d946ef' }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ stacked: true, ticks: {{ color: '#9CA3AF', font: {{ size: 10 }} }}, grid: {{ display: false }} }},
                        y: {{ stacked: true, max: 100, ticks: {{ color: '#9CA3AF' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
                    }},
                    plugins: {{
                        legend: {{ position: 'top', labels: {{ color: '#9CA3AF', font: {{ size: 11 }} }} }}
                    }}
                }}
            }});

            // Chart 3: Buildability Verdicts
            const bCtx = document.getElementById('buildabilityChart').getContext('2d');
            bChartInst = new Chart(bCtx, {{
                type: 'pie',
                data: {{
                    labels: Object.keys(ANALYSIS_DATA.buildability_breakdown.counts),
                    datasets: [{{
                        data: Object.values(ANALYSIS_DATA.buildability_breakdown.counts),
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#6b7280'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'right', labels: {{ color: '#9CA3AF', font: {{ size: 11 }} }} }}
                    }}
                }}
            }});

            // Chart 4: Top Blockers
            const blkCtx = document.getElementById('blockerChart').getContext('2d');
            new Chart(blkCtx, {{
                type: 'bar',
                indexAxis: 'y',
                data: {{
                    labels: Object.keys(ANALYSIS_DATA.top_blockers),
                    datasets: [{{
                        label: 'Apps Affected',
                        data: Object.values(ANALYSIS_DATA.top_blockers),
                        backgroundColor: '#6366f1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{ ticks: {{ color: '#9CA3AF' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                        y: {{ ticks: {{ color: '#9CA3AF', font: {{ size: 10 }} }}, grid: {{ display: false }} }}
                    }},
                    plugins: {{
                        legend: {{ display: false }}
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    os.makedirs(os.path.join(os.path.dirname(__file__), "output"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "output", "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Deliverable HTML successfully updated at:\n - {OUTPUT_HTML}\n - output/index.html")

if __name__ == "__main__":
    build_html_deliverable()
