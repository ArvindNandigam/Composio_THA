import os
import json
import time
from agent.models import AppInput
from agent.researcher import run_research_batch

INPUT_FILE = os.path.join(os.path.dirname(__file__), "data", "apps_input.json")

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        apps_data = json.load(f)

    apps = [AppInput(**a) for a in apps_data]
    print(f"==================================================")
    print(f"Starting Composio Research Agent across {len(apps)} apps")
    print(f"==================================================")

    start_time = time.time()
    results = run_research_batch(apps, resume=True)
    elapsed = time.time() - start_time

    print(f"\n==================================================")
    print(f"Research Completed! Researched {len(results)} apps in {elapsed:.1f}s")
    print(f"Results saved to data/research_results.json")
    print(f"==================================================")

if __name__ == "__main__":
    main()
