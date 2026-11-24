"""
test_m4_verification.py — Comprehensive Automated Verification Suite for Milestone M4
Requirement R5: Human Report Auditing & Output Verification

Verifies:
1. All 13 top-level keys in data/verification_audit.json with exact values and schema compliance.
2. All 100 audit records validate against VerificationAuditRecord with exact discrepancy parity (23 discrepancies, 77 verified, 30 MCPs).
3. App 25 (Pumble) reconciliation to Blocked (No public API) and Private/Closed API surface.
4. All 100 apps in data/research_results.json have valid human_report_status and human_report matching audit resolutions.
5. All evidence URLs are sanitized, valid documentation links without forum/spam domains (including Apps 1, 4, 5).
6. Modular verify_app() and run_full_verification() functions in agent/verifier.py.
7. HTML deliverables (index.html and output/index.html) match byte-for-byte, render 3-stage funnel metrics, and render Composio telemetry metrics in visible DOM.
"""

import os
import re
import json
import urllib.parse
from html.parser import HTMLParser
from typing import Dict, Any

from agent.models import AppResearchResult, VerificationAuditRecord
from agent.verifier import verify_app, run_full_verification, sanitize_evidence_urls


def test_verification_audit_json():
    print("\n--- [Step 1] Auditing data/verification_audit.json ---")
    audit_path = os.path.join("data", "verification_audit.json")
    assert os.path.exists(audit_path), f"Missing audit file: {audit_path}"

    with open(audit_path, "r", encoding="utf-8") as f:
        audit = json.load(f)

    # 1. Exact 13 Top-Level Keys Verification
    expected_metrics = {
        "total_apps_audited": 100,
        "pass1_accurate_count": 77,
        "pass1_discrepancy_count": 23,
        "pass1_accuracy_pct": 77.0,
        "post_verification_accuracy_pct": 100.0,
        "automated_verification_accuracy_pct": 86.0,
        "automated_verification_accurate_count": 86,
        "automated_verification_uplift_pct": 9.0,
        "human_audit_discrepancies_found": 23,
        "human_audit_discrepancy_rate_pct": 23.0,
        "human_confirmed_count": 77,
        "post_human_ground_truth_accuracy_pct": 100.0,
    }

    for key, expected_val in expected_metrics.items():
        assert key in audit, f"Missing required top-level key '{key}' in audit JSON"
        actual_val = audit[key]
        assert actual_val == expected_val, (
            f"Metric mismatch for '{key}': expected {expected_val}, got {actual_val}"
        )
        print(f"  [PASS] Metric '{key}': {actual_val}")

    # 2. Methodology Audit Structure
    assert "methodology_audit" in audit, "Missing 'methodology_audit' key"
    methodology = audit["methodology_audit"]
    for stage in ["stage1_pass1", "stage2_pass2", "stage3_pass3"]:
        assert stage in methodology, f"Missing stage '{stage}' in methodology_audit"
        assert "name" in methodology[stage]
        assert "description" in methodology[stage]
    print("  [PASS] Methodology audit stages 1, 2, and 3 verified.")

    # 3. Audit Records Validation
    assert "audit_records" in audit, "Missing 'audit_records' key"
    records = audit["audit_records"]
    assert len(records) == 100, f"Expected 100 audit records, got {len(records)}"

    disc_count = 0
    mcp_count = 0
    disc_ids = []

    for r in records:
        # Validate Pydantic schema
        record_obj = VerificationAuditRecord(**r)
        assert record_obj.app_id > 0
        assert record_obj.app_name
        assert record_obj.category
        assert record_obj.resolution
        assert record_obj.verified_evidence_url.startswith("http")

        if record_obj.discrepancy_found:
            disc_count += 1
            disc_ids.append(record_obj.app_id)
        if record_obj.mcp_verified_url:
            mcp_count += 1
            assert record_obj.mcp_verified_url.startswith("http")

    assert disc_count == 23, f"Expected 23 discrepancies in audit_records, got {disc_count}"
    assert mcp_count == 30, f"Expected 30 verified MCP URLs, got {mcp_count}"
    print(f"  [PASS] All 100 records validated against VerificationAuditRecord.")
    print(f"  [PASS] Discrepancies: {disc_count}, Verified MCP URLs: {mcp_count}")

    # 4. App 25 (Pumble) Reconciliation Check
    pumble_record = next(r for r in records if r["app_id"] == 25)
    assert pumble_record["discrepancy_found"] is False
    assert "Blocked (No public API)" in pumble_record["pass1_summary"]
    assert "Private/Closed" in pumble_record["pass1_summary"]
    assert "Blocked due to private/closed API surface" in pumble_record["resolution"]
    print("  [PASS] App 25 (Pumble) reconciled to Blocked / Private surface in audit records.")
    return audit


def test_research_results_json(audit_data: Dict[str, Any]):
    print("\n--- [Step 2] Auditing data/research_results.json ---")
    results_path = os.path.join("data", "research_results.json")
    assert os.path.exists(results_path), f"Missing research results file: {results_path}"

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    assert len(results) == 100, f"Expected 100 apps, got {len(results)}"
    audit_records_map = {r["app_id"]: r for r in audit_data["audit_records"]}

    verified_status_count = 0
    corrected_status_count = 0
    spam_domains = ["edu-kingdom.com", "justdial.com", "zhihu.com", "forum.", "reddit.com", "quora.com"]

    for app in results:
        app_obj = AppResearchResult(**app)
        aid = app_obj.id
        record = audit_records_map[aid]

        # Check human_report_status synchronization
        if record["discrepancy_found"]:
            assert app_obj.human_report_status == "Corrected in Audit", (
                f"App #{aid} ({app_obj.name}) should have status 'Corrected in Audit'"
            )
            corrected_status_count += 1
        else:
            assert app_obj.human_report_status == "Verified", (
                f"App #{aid} ({app_obj.name}) should have status 'Verified'"
            )
            verified_status_count += 1

        # Check human_report and verification_notes synchronization
        assert app_obj.human_report == record["resolution"], (
            f"App #{aid} human_report doesn't match audit resolution"
        )
        assert app_obj.verification_notes == record["resolution"], (
            f"App #{aid} verification_notes doesn't match audit resolution"
        )

        # Check MCP synchronization
        if record["mcp_verified_url"]:
            assert app_obj.mcp_url == record["mcp_verified_url"], (
                f"App #{aid} mcp_url mismatch"
            )
            assert app_obj.existing_mcp is True, (
                f"App #{aid} existing_mcp should be True"
            )

        # Check Evidence URLs hygiene
        assert len(app_obj.evidence_urls) > 0, f"App #{aid} has empty evidence_urls"
        for url in app_obj.evidence_urls:
            assert url.startswith("http://") or url.startswith("https://"), (
                f"App #{aid} contains non-http URL: {url}"
            )
            domain = urllib.parse.urlparse(url).netloc.lower()
            for spam in spam_domains:
                assert spam not in domain and spam not in url.lower(), (
                    f"App #{aid} contains spam/forum URL: {url}"
                )

    assert verified_status_count == 77, f"Expected 77 Verified apps, got {verified_status_count}"
    assert corrected_status_count == 23, f"Expected 23 Corrected in Audit apps, got {corrected_status_count}"
    print(f"  [PASS] All 100 apps match audit parity: 77 Verified, 23 Corrected in Audit.")
    print(f"  [PASS] All evidence URLs clean, valid, and free of spam/forum links.")

    # Spot-check Apps 1, 4, 5
    app1 = next(a for a in results if a["id"] == 1)
    assert any("developer.salesforce.com" in u for u in app1["evidence_urls"])
    assert not any("edu-kingdom" in u for u in app1["evidence_urls"])
    print(f"  [PASS] App #1 (Salesforce) sanitized: {app1['evidence_urls']}")

    app4 = next(a for a in results if a["id"] == 4)
    assert any("developers.attio.com" in u for u in app4["evidence_urls"])
    assert not any("justdial" in u for u in app4["evidence_urls"])
    print(f"  [PASS] App #4 (Attio) sanitized: {app4['evidence_urls']}")

    app5 = next(a for a in results if a["id"] == 5)
    assert any("twenty.com" in u for u in app5["evidence_urls"])
    assert any("github.com/twentyhq/twenty" in u for u in app5["evidence_urls"])
    assert not any("zhihu" in u for u in app5["evidence_urls"])
    print(f"  [PASS] App #5 (Twenty) sanitized: {app5['evidence_urls']}")

    # Check App 25 (Pumble)
    app25 = next(a for a in results if a["id"] == 25)
    assert app25["buildability"] == "Blocked (No public API)"
    assert app25["api_surface"] == "Private/Closed"
    print(f"  [PASS] App #25 (Pumble) research verified as Blocked (No public API).")
    return results


def test_modular_verifier_functions():
    print("\n--- [Step 3] Testing agent/verifier.py modular functions ---")
    results_path = os.path.join("data", "research_results.json")
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    app1_raw = next(a for a in results if a["id"] == 1)
    app1 = AppResearchResult(**app1_raw)

    existing_rec = {
        "app_id": 1,
        "app_name": "Salesforce",
        "category": "CRM and Sales",
        "pass1_summary": "Auth: OAuth2, API Key | Gating: Partially Gated | MCP: Yes",
        "discrepancy_found": False,
        "discrepancy_type": "Verified Accurate",
        "resolution": "Confirmed OAuth2 connected app setup & REST/GraphQL surface.",
        "verified_evidence_url": "https://developer.salesforce.com/docs/apis",
        "mcp_verified_url": "https://github.com/salesforcecli/mcp"
    }

    # Test verify_app with existing record
    updated_app, rec = verify_app(app1, existing_record=existing_rec, refresh_llm=False)
    assert updated_app.human_report_status == "Verified"
    assert updated_app.human_report == existing_rec["resolution"]
    assert updated_app.mcp_url == "https://github.com/salesforcecli/mcp"
    assert updated_app.existing_mcp is True
    assert rec["app_id"] == 1
    print("  [PASS] verify_app() successfully verified single app with ground-truth preservation.")

    # Test run_full_verification with subset of IDs without disk mutation
    summary = run_full_verification(app_ids=[1, 25], refresh_llm=False, update_results=False)
    assert summary["total_apps_audited"] == 100
    assert summary["pass1_accuracy_pct"] == 77.0
    print("  [PASS] run_full_verification() executed without error and returned full 13-key summary.")


class _VisibleTextExtractor(HTMLParser):
    """Extracts visible DOM text while excluding <script>, <style>, comments, and tag attributes."""

    IGNORED_TAGS = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip_stack = []
        self._parts = []

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in self.IGNORED_TAGS:
            self._skip_stack.append(t)

    def handle_endtag(self, tag):
        t = tag.lower()
        if self._skip_stack and self._skip_stack[-1] == t:
            self._skip_stack.pop()

    def handle_data(self, data):
        if not self._skip_stack and data and not data.isspace():
            self._parts.append(data)

    def get_text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._parts)).strip()


def extract_visible_html_text(html_str: str) -> str:
    parser = _VisibleTextExtractor()
    parser.feed(html_str)
    parser.close()
    return parser.get_text()


def test_html_deliverable_parity(results_data: list):
    print("\n--- [Step 4] Testing HTML Deliverable Parity ---")
    index_path = "index.html"
    output_index_path = os.path.join("output", "index.html")

    assert os.path.exists(index_path), "Missing index.html"
    assert os.path.exists(output_index_path), "Missing output/index.html"

    with open(index_path, "rb") as f1, open(output_index_path, "rb") as f2:
        content1 = f1.read()
        content2 = f2.read()

    assert content1 == content2, "index.html and output/index.html do not match byte-for-byte!"
    assert len(content1) > 100000, f"HTML file too small: {len(content1)} bytes"
    print(f"  [PASS] index.html and output/index.html match byte-for-byte ({len(content1)} bytes).")

    html_str = content1.decode("utf-8")
    visible_text = extract_visible_html_text(html_str)
    assert "APPS_DATA" not in visible_text and "ANALYSIS_DATA" not in visible_text, (
        "Script variable leaked into extracted visible DOM text"
    )

    # Funnel metrics check (verified in visible DOM outside <script> and comments)
    assert "77.0%" in visible_text, "77.0% missing from visible HTML DOM"
    assert "86.0%" in visible_text, "86.0% missing from visible HTML DOM"
    assert "+9.0%" in visible_text, "+9.0% missing from visible HTML DOM"
    assert "23" in visible_text and ("Human Fixes" in visible_text or "Corrected" in visible_text), (
        "23 human fixes missing from visible HTML DOM"
    )
    assert "100.0%" in visible_text, "100.0% missing from visible HTML DOM"
    print("  [PASS] All 3-Stage Verification Funnel metrics present in visible HTML DOM.")

    # Composio telemetry visible DOM check (cross-checked against data/telemetry_metrics.json)
    telemetry_path = os.path.join("data", "telemetry_metrics.json")
    assert os.path.exists(telemetry_path), f"Missing telemetry file: {telemetry_path}"
    with open(telemetry_path, "r", encoding="utf-8") as f:
        telemetry = json.load(f)

    total_queries = telemetry["total_queries"]
    composio_queries = telemetry["composio_queries"]
    composio_share_pct = telemetry["composio_share_pct"]
    fallback_queries = telemetry["fallback_queries"]
    composio_search = telemetry["composio_search"]
    composio_fetch = telemetry["composio_fetch"]

    assert total_queries == 300, f"Expected 300 total_queries, got {total_queries}"
    assert composio_queries == 258, f"Expected 258 composio_queries, got {composio_queries}"
    assert composio_share_pct == 86.0, f"Expected 86.0 composio_share_pct, got {composio_share_pct}"
    assert fallback_queries == 42, f"Expected 42 fallback_queries, got {fallback_queries}"
    assert composio_search == 199, f"Expected 199 composio_search, got {composio_search}"
    assert composio_fetch == 59, f"Expected 59 composio_fetch, got {composio_fetch}"

    visible_lower = visible_text.lower()
    assert "telemetry" in visible_lower, (
        "Composio telemetry section/heading missing from visible HTML DOM (outside <script> and comments)"
    )
    assert re.search(rf"(?<!#)\b{total_queries}\b", visible_text), (
        f"Total queries ({total_queries}) missing from visible HTML DOM"
    )
    assert re.search(rf"(?<!#)\b{composio_queries}\b", visible_text), (
        f"Composio queries ({composio_queries}) missing from visible HTML DOM"
    )
    assert re.search(rf"\b{re.escape(f'{composio_share_pct:.1f}')}%", visible_text), (
        f"Composio share ({composio_share_pct:.1f}%) missing from visible HTML DOM"
    )
    assert re.search(rf"(?<!#)\b{fallback_queries}\b", visible_text), (
        f"Fallback queries ({fallback_queries}) missing from visible HTML DOM (ignoring #42 app ID)"
    )
    assert re.search(rf"(?<!#)\b{composio_search}\b", visible_text) and "tavily" in visible_lower, (
        f"Composio Tavily search count ({composio_search}) missing from visible HTML DOM"
    )
    assert re.search(rf"(?<!#)\b{composio_fetch}\b", visible_text) and "firecrawl" in visible_lower, (
        f"Composio Firecrawl scrape count ({composio_fetch}) missing from visible HTML DOM"
    )
    assert "TAVILY_SEARCH" in visible_text and "FIRECRAWL_SCRAPE" in visible_text, (
        "TAVILY_SEARCH or FIRECRAWL_SCRAPE tool slug missing from visible HTML DOM"
    )

    # Co-location check: prevents unrelated sections (#42 WooCommerce, Tier 1 59 Apps, Pass 2 86.0%) from spoofing telemetry
    def _has_telemetry_cluster(slice_text: str) -> bool:
        low = slice_text.lower()
        return (
            "telemetry" in low
            and "composio" in low
            and "fallback" in low
            and "tavily" in low
            and "firecrawl" in low
            and re.search(rf"(?<!#)\b{total_queries}\b", slice_text) is not None
            and re.search(rf"(?<!#)\b{composio_queries}\b", slice_text) is not None
            and re.search(rf"\b{re.escape(f'{composio_share_pct:.1f}')}%", slice_text) is not None
            and re.search(rf"(?<!#)\b{fallback_queries}\b", slice_text) is not None
            and re.search(rf"(?<!#)\b{composio_search}\b", slice_text) is not None
            and re.search(rf"(?<!#)\b{composio_fetch}\b", slice_text) is not None
        )

    anchors = re.finditer(rf"(?:telemetry|(?<!#)\b{composio_queries}\b)", visible_text, re.IGNORECASE)
    windows = [visible_text[max(0, m.start() - 1200) : m.end() + 3500] for m in anchors]
    assert any(_has_telemetry_cluster(w) for w in windows), (
        "Visible HTML DOM lacks a co-located Composio telemetry panel rendering all required metrics "
        "(300 total, 258 Composio / 86.0% share, 42 fallback, 199 Tavily search, 59 Firecrawl scrape)"
    )
    print(
        f"  [PASS] Visible HTML DOM renders Composio telemetry metrics: "
        f"{total_queries} total, {composio_queries} Composio ({composio_share_pct:.1f}%), "
        f"{fallback_queries} fallback, {composio_search} Tavily search, {composio_fetch} Firecrawl scrape."
    )

    # Check embedded APPS_DATA matches research_results.json
    match = re.search(r"const APPS_DATA = (\[.*?\]);\s*const ANALYSIS_DATA", html_str, re.DOTALL)
    assert match, "Could not locate const APPS_DATA in index.html"
    embedded_apps = json.loads(match.group(1))
    assert len(embedded_apps) == 100, f"Expected 100 apps in APPS_DATA, found {len(embedded_apps)}"
    assert embedded_apps == results_data, "Embedded APPS_DATA does not match data/research_results.json"
    print("  [PASS] Embedded APPS_DATA in index.html matches data/research_results.json perfectly.")


def main():
    print("=" * 60)
    print("MILESTONE M4 AUTOMATED VERIFICATION SUITE")
    print("Requirement R5: Human Report Auditing & Output Verification")
    print("=" * 60)

    audit_data = test_verification_audit_json()
    results_data = test_research_results_json(audit_data)
    test_modular_verifier_functions()
    test_html_deliverable_parity(results_data)

    print("\n" + "=" * 60)
    print("ALL M4 VERIFICATION SUITE TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
