"""
DevSecOps Quality Gate Evaluator for Bandit SAST Reports.
Author: Dhio Patty Alexander (0110225006)

This script parses Bandit JSON output and enforces organizational security thresholds.
Policy:
- High Severity Tolerance: 0 (Strict)
- Medium Severity Tolerance: 0 (Strict)
- Low Severity: Allowed (Warning logged)
"""

import sys
import json
import os
from typing import Dict, Any


def evaluate_quality_gate(report_path: str) -> bool:
    print("=" * 65)
    print("           DEVSECOPS QUALITY GATE EVALUATION REPORT             ")
    print("=" * 65)

    if not os.path.exists(report_path):
        print(f"[ERROR] SAST report file not found at: {report_path}")
        return False

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON report: {e}")
        return False

    metrics = data.get("metrics", {}).get("_totals", {})
    results = data.get("results", [])

    high_sev = metrics.get("SEVERITY.HIGH", 0)
    med_sev = metrics.get("SEVERITY.MEDIUM", 0)
    low_sev = metrics.get("SEVERITY.LOW", 0)
    undefined_sev = metrics.get("SEVERITY.UNDEFINED", 0)

    loc = metrics.get("loc", 0)
    total_issues = len(results)

    print(f"Target Scanned Source Lines (LOC) : {loc}")
    print(f"Total Security Findings Detected  : {total_issues}")
    print("-" * 65)
    print(f"  [-] High Severity Findings     : {high_sev} (Threshold Max: 0)")
    print(f"  [-] Medium Severity Findings   : {med_sev} (Threshold Max: 0)")
    print(f"  [-] Low Severity Findings      : {low_sev} (Threshold Max: 5)")
    print(f"  [-] Undefined Findings         : {undefined_sev}")
    print("-" * 65)

    if results:
        print("\nDETAILED FINDINGS BREAKDOWN:")
        for idx, issue in enumerate(results, 1):
            sev = issue.get("issue_severity", "UNKNOWN")
            conf = issue.get("issue_confidence", "UNKNOWN")
            test_id = issue.get("test_id", "N/A")
            filename = issue.get("filename", "N/A")
            line = issue.get("line_number", "N/A")
            text = issue.get("issue_text", "")
            print(f"  [{idx}] [{sev} / Conf: {conf}] {test_id} at {filename}:{line}")
            print(f"      Description: {text}")

    print("\n" + "=" * 65)

    # Gate Evaluation Policy
    passed = True
    reasons = []

    if high_sev > 0:
        passed = False
        reasons.append(f"Found {high_sev} HIGH severity vulnerabilities (Policy allows: 0).")

    if med_sev > 0:
        passed = False
        reasons.append(f"Found {med_sev} MEDIUM severity vulnerabilities (Policy allows: 0).")

    if low_sev > 5:
        passed = False
        reasons.append(f"Found {low_sev} LOW severity vulnerabilities exceeding limit (Max: 5).")

    if passed:
        print(">>> STATUS: [ QUALITY GATE PASSED ] <<<")
        print("All security thresholds have been satisfied. Ready for deployment!")
        print("=" * 65)
        return True
    else:
        print(">>> STATUS: [ QUALITY GATE FAILED ] <<<")
        print("The build is blocked due to policy violations:")
        for r in reasons:
            print(f"  - {r}")
        print("=" * 65)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quality_gate.py <path_to_bandit_report.json>")
        sys.exit(1)

    file_path = sys.argv[1]
    is_passed = evaluate_quality_gate(file_path)

    if not is_passed:
        sys.exit(1)
    sys.exit(0)
