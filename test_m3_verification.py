import json
import os
from agent.models import AppResearchResult
from agent.analyzer import analyze_patterns
from generate_html import build_html_deliverable

def test_m3():
    print("--- 1. Testing data/research_results.json ---")
    results_path = os.path.join("data", "research_results.json")
    assert os.path.exists(results_path), "research_results.json does not exist"
    
    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 100, f"Expected 100 apps, got {len(data)}"
    print(f"Total apps: {len(data)}")

    # Verify Pydantic validation
    for item in data:
        res = AppResearchResult(**item)
        assert res.id > 0
        assert len(res.name) > 0
        assert isinstance(res.auth_methods, list)
        assert len(res.evidence_urls) > 0
        assert res.human_report_status in ["Verified", "Corrected in Audit"], f"Invalid human_report_status: {res.human_report_status} for {res.name}"
        assert res.human_report is not None and len(res.human_report) > 0, f"Missing human_report for {res.name}"

    print("All 100 apps passed Pydantic validation and have human_report / human_report_status intact.")

    # Inspect the 5 freshly researched apps
    for app_id in [1, 2, 3, 4, 5]:
        item = next(a for a in data if a["id"] == app_id)
        print(f"  App #{item['id']} {item['name']}: Verdict={item['buildability']}, Auth={item['auth_methods']}, MCP={item['existing_mcp']}, HR_Status={item['human_report_status']}")

    print("\n--- 2. Testing agent/analyzer.py execution ---")
    analysis = analyze_patterns()
    assert analysis["total_apps"] == 100
    assert "composio_viable_pct" in analysis
    assert "composio_viable_count" in analysis
    assert "greenfield_opportunity_pct" in analysis
    print(f"Analysis successfully refreshed:")
    print(f"  Total apps: {analysis['total_apps']}")
    print(f"  Composio viable: {analysis['composio_viable_count']} ({analysis['composio_viable_pct']}%)")
    print(f"  Greenfield opportunity: {analysis['greenfield_opportunity_count']} ({analysis['greenfield_opportunity_pct']}%)")
    print(f"  Existing MCP count: {analysis['mcp_ecosystem']['existing_mcp_count']}")

    print("\n--- 3. Testing generate_html.py execution ---")
    build_html_deliverable()
    assert os.path.exists("index.html"), "index.html missing"
    assert os.path.exists(os.path.join("output", "index.html")), "output/index.html missing"

    root_size = os.path.getsize("index.html")
    output_size = os.path.getsize(os.path.join("output", "index.html"))
    assert root_size > 50000, f"index.html too small: {root_size} bytes"
    assert root_size == output_size, f"index.html ({root_size}) and output/index.html ({output_size}) size mismatch"
    print(f"index.html size: {root_size} bytes, matches output/index.html exactly.")

    # Check that index.html contains key elements
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    assert "Composio Buildable" in html
    assert f"{analysis['buildability_breakdown']['composio_viable_pct']}%" in html
    assert "Candidate Submission Dossier" in html
    assert "Arvind Nandigam" in html
    assert "Salesforce" in html
    assert "Twenty" in html
    print("index.html content checks passed successfully!")

    print("\n==================================================")
    print("ALL M3 VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_m3()
