import json
import os
import argparse
import subprocess
import tempfile
from datetime import datetime

TARGET_REPOS_FILE = os.path.join("data", "target_repos.json")
SCAN_STATE_FILE = os.path.join("data", "scan_state.json")
REPORTS_DIR = "reports"

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_value

def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def scan_repo(repo_url):
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    findings = []

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, repo_name)
        # Shallow clone
        subprocess.run(["git", "clone", "--depth", "1", repo_url, repo_path], capture_output=True)

        # We need a robust way to scan. Instead of finding all files and cat'ing them to CLI (which might break on large repos)
        # we can use the detector directly or through CLI if we implement directory scanning, but currently cli.py only takes single file.
        # Let's import detector and scan files manually.

        import sys

        # We need to make sure the detector path is in sys.path
        # When run from root, os.path.abspath(".") should be the root.
        # But let's add the root explicitly based on this script's location.
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)

        import detector
        import report
        from detector import SecretDetector

        try:
            det = SecretDetector()
        except Exception as e:
            print(f"Error initializing detector: {e}")
            return findings

        for root, dirs, files in os.walk(repo_path):
            if '.git' in root:
                continue
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            f_list = det.scan(line, source=file, line_number=i+1)
                            # apply obfuscation manually or let the report handle it.
                            # We can just collect them.
                            for finding in f_list:
                                findings.append({
                                    "rule_id": finding.rule_id,
                                    "source": finding.source,
                                    "line_number": finding.line_number,
                                    # Always use redacted value for public reports!
                                    "value": finding.redacted_value,
                                    "severity": finding.severity
                                })
                except Exception as e:
                    pass

    return findings

def generate_report(results):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_file = os.path.join(REPORTS_DIR, f"report_{date_str}.md")

    with open(report_file, "w") as f:
        f.write(f"# Daily Secret Scan Report ({date_str})\n\n")
        f.write("This report contains anonymized findings from automated secret scans.\n\n")

        for repo_url, findings in results.items():
            f.write(f"## {repo_url}\n")
            if not findings:
                f.write("No secrets found.\n\n")
            else:
                f.write(f"Found {len(findings)} secrets:\n")
                f.write("| Rule ID | Source | Line | Redacted Value | Severity |\n")
                f.write("|---|---|---|---|---|\n")
                for finding in findings:
                    f.write(f"| {finding['rule_id']} | {finding['source']} | {finding['line_number']} | `{finding['value']}` | {finding['severity']} |\n")
                f.write("\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=3, help="Number of repos to scan")
    args = parser.parse_args()

    repos = load_json(TARGET_REPOS_FILE, [])
    if not repos:
        print(f"No repositories found in {TARGET_REPOS_FILE}. Please run tools/curate_repos.py first.")
        return

    state = load_json(SCAN_STATE_FILE, {"last_index": 0})
    start_index = state.get("last_index", 0)

    if start_index >= len(repos):
        start_index = 0 # loop around

    end_index = min(start_index + args.count, len(repos))
    repos_to_scan = repos[start_index:end_index]

    results = {}
    for repo in repos_to_scan:
        print(f"Scanning {repo}...")
        findings = scan_repo(repo)
        results[repo] = findings

    generate_report(results)

    # Update state
    state["last_index"] = end_index if end_index < len(repos) else 0
    save_json(SCAN_STATE_FILE, state)
    print("Daily scan complete.")

if __name__ == "__main__":
    main()
