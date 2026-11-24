import os
import sys
import json
import time
import argparse
from dotenv import load_dotenv
from agent.models import AppInput
from agent.researcher import run_research_batch, research_app
from agent.analyzer import analyze_patterns
from agent.tools import get_tool_telemetry, save_telemetry_metrics, reset_tool_telemetry
from generate_html import build_html_deliverable

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DEFAULT_INPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "apps_input.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "data", "research_results.json")
TELEMETRY_FILE = os.path.join(os.path.dirname(__file__), "data", "telemetry_metrics.json")


def print_telemetry_summary():
    """Outputs a clean ASCII telemetry summary box and persists metrics to disk."""
    save_telemetry_metrics(TELEMETRY_FILE)
    telemetry = get_tool_telemetry()

    print("\n+============================================================+")
    print("|                COMPOSIO EXECUTION TELEMETRY                |")
    print("+============================================================+")
    print(f"| Total Queries:            {telemetry.get('total_queries', 0):<32} |")
    print(f"| Composio Handled Queries: {telemetry.get('composio_queries', 0):<32} |")
    print(f"| Fallback Queries:         {telemetry.get('fallback_queries', 0):<32} |")
    print(f"| Composio Share %:         {str(telemetry.get('composio_share_pct', 0.0)) + '%':<32} |")
    print("+------------------------------------------------------------+")
    print("| Provider Breakdown:                                        |")
    for provider, count in sorted(telemetry.get("providers", {}).items()):
        print(f"|   - {provider:<24} : {count:<25} |")
    print("+============================================================+")
    print(f"Telemetry metrics saved to: {TELEMETRY_FILE}\n")


def main():
    parser = argparse.ArgumentParser(description="Composio SaaS Research Agent: Research 100 or custom apps.")
    parser.add_argument("--name", type=str, help="Single app name to research (e.g. 'PostHog')")
    parser.add_argument("--category", type=str, default="Developer, Infra and Data platforms", help="Category for single app")
    parser.add_argument("--hint", type=str, default=None, help="Domain or doc hint (e.g. 'posthog.com')")
    parser.add_argument("--input", type=str, default=DEFAULT_INPUT_FILE, help="Path to input JSON catalog")
    parser.add_argument("--apps", type=int, default=None, help="Number of apps to research from catalog (e.g. 100)")
    parser.add_argument("--app-id", "--id", type=int, default=None, help="Specific app ID to research from catalog (e.g. 1)")
    parser.add_argument("--resume", action="store_true", default=False, help="Resume from cache and skip already researched apps")
    parser.add_argument("--no-cache", "--refresh", action="store_true", dest="no_cache", default=False, help="Do not skip cached apps; re-research and refresh existing data")
    parser.add_argument("--no-reset-telemetry", action="store_false", dest="reset_telemetry", default=True, help="Do not reset telemetry tracker before run")
    parser.add_argument("--workers", "-w", type=int, default=int(os.getenv("MAX_CONCURRENT_REQUESTS", "3")), help="Number of concurrent research worker threads (default: 3)")
    parser.add_argument("--verify", action="store_true", help="Run automated verification loop on researched apps")
    parser.add_argument("--no-rebuild", action="store_true", help="Skip re-running analysis and HTML generation")
    args = parser.parse_args()

    # Reset telemetry at start of execution by default to cleanly track this run
    if args.reset_telemetry:
        reset_tool_telemetry()

    # Case 1: Single ad-hoc app passed via CLI
    if args.name:
        print(f"==================================================")
        print(f"Researching Single Custom App: {args.name}")
        print(f"Category: {args.category} | Hint: {args.hint} | Model: {GEMINI_MODEL}")
        print(f"==================================================")

        # Determine next ID
        existing = []
        if os.path.exists(RESULTS_FILE):
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        next_id = max([a.get("id", 0) for a in existing], default=100) + 1

        app_input = AppInput(
            id=next_id,
            name=args.name,
            category=args.category,
            hint=args.hint or f"{args.name.lower().replace(' ', '')}.com"
        )

        res = research_app(app_input)
        print(f"\nCompleted research for {args.name}:")
        print(f"  Auth: {res.auth_methods}")
        print(f"  Gating: {res.self_serve}")
        print(f"  Verdict: {res.buildability}")
        print(f"  Evidence: {res.evidence_urls}")

        # Append to results
        existing_dict = {a["id"]: a for a in existing}
        existing_dict[next_id] = res.model_dump()
        with open(RESULTS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(existing_dict.values()), f, indent=2)

        print(f"Saved custom app #{next_id} to {RESULTS_FILE}")

        print_telemetry_summary()

        if not args.no_rebuild:
            print("\nRe-running pattern analyzer and rebuilding dashboard...")
            analyze_patterns()
            build_html_deliverable()
        return

    # Case 2: Batch file (default or custom JSON)
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found!")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        apps_data = json.load(f)

    apps = [AppInput(**a) for a in apps_data]
    if args.app_id is not None:
        apps = [a for a in apps if a.id == args.app_id]
        if not apps:
            print(f"Error: App ID #{args.app_id} not found in catalog {args.input}!")
            sys.exit(1)
    elif args.apps is not None:
        apps = apps[:args.apps]

    # Mode determination: fresh research unless --resume is requested without --no-cache
    should_resume = args.resume and not args.no_cache

    print(f"==================================================")
    print(f"Starting Composio Research Agent across {len(apps)} apps")
    print(f"Catalog file: {args.input}")
    print(f"LLM Model:    {GEMINI_MODEL}")
    print(f"Cache mode:   {'RESUME (cached skipped)' if should_resume else 'RESEARCH PIPELINE EXECUTION (fresh pass)'}")
    print(f"==================================================")

    start_time = time.time()
    results = run_research_batch(apps, resume=should_resume, max_workers=args.workers)
    elapsed = time.time() - start_time

    print(f"\n==================================================")
    print(f"Research Completed! Researched {len(results)} apps in {elapsed:.1f}s")
    print(f"Results saved to {RESULTS_FILE}")
    print(f"==================================================")

    # Save and output clean ASCII execution telemetry
    print_telemetry_summary()

    if args.verify:
        print("\n==================================================")
        print("Running Automated Verification Loop...")
        print("==================================================")
        from agent.verifier import run_full_verification
        run_full_verification()

    if not args.no_rebuild:
        print("\nRe-running pattern analyzer and rebuilding dashboard...")
        analyze_patterns()
        build_html_deliverable()

if __name__ == "__main__":
    main()
