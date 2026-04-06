# Instructions for Maintaining the Pattern Library

The pattern library is the heart of the detector—every new rule flows through normalization, validation, deduplication, and test-data generation before it enters the `data/` taxonomy. This document captures the current workflow, aligned with the "Pattern Library Expansion" and "Code Health & Detection Refinement" plans.

## 1. Acquire and Organize Sources

1.  Clone the upstream pattern repositories (examples):
    ```bash
    git clone https://github.com/advanced-security/secret-scanning-tools
    git clone https://github.com/advanced-security/secret-scanning-custom-patterns
    ```
2.  Review each rule's metadata and decide which internal category it belongs to. Use the taxonomy in `data/` (e.g., `api_keys`, `cloud_credentials`, `database_credentials`, `infrastructure`, `tokens`, `private_keys`) as the target.
3.  Keep rule metadata sanitized—avoid embedding real secrets. Use the `DUMMY_IGNORE` token when you need non-matching placeholders in `test_data.json`.

## 2. Normalize & Migrate

1.  Run `python tools/migrate_patterns.py`. This script:
    * harmonizes keys (e.g., `regex`, `keywords`, `entropy`) so every rule shares a common schema.
    * injects per-rule `entropy_factor`, `min_entropy`, and `confidence` defaults aligned with the detection plan.
    * rewrites regex anchoring, removes unsupported constructs, and ensures RE2 compatibility.
    * maps external categories (AWS, Mongo, Terraform, etc.) into the internal taxonomy.
2.  If you need to adjust entropy heuristics manually, `tools/migrate_entropy_factor.py` can scan `data/**/*.json` and rebalance thresholds before committing the updated rule set.

## 3. Deduplicate & Generate Test Data

1.  Run `python tools/deduplicate_rules.py` to merge identical regexes and keep the rule database unique. This tool also updates metadata such as the canonical `id` and `category`.
2.  Rebuild the test corpus with `python tools/generate_test_data.py`. It emits sanitized `test_data.json` files with base64-encoded samples for every rule, plus negative controls. The script also contains custom generators for complex secrets (Stripe, Twilio, IBAN, etc.).

## 4. Validate Quality & Safety

1.  Run `python tools/regex_lint.py` to catch syntax issues, missing keywords, or rules that violate the new schema.
2.  Use `python tools/run_safe_regex.py` and `python tools/run_redoctor.py` to guard against ReDoS and exponential backtracking.
3.  Optionally run `python tools/run_regexploit.py` if you are expanding coverage for tricky patterns (e.g., multiline private keys).

## 5. Exercise Detection & Documentation

1.  Run the full verification suite (including Git and Performance tests):
    ```bash
    pytest tests/test_detector.py tests/test_obfuscator.py tests/test_new_rules.py tests/test_git_engine.py tests/test_performance.py
    ```
2.  Verify Git-specific flows:
    ```bash
    pytest tests/test_acceptance.py
    ```
3.  Update documentation (README, release notes) with:
    * latest CLI options and Git integration workflows.
    * performance benchmarks for parallel/cached modes.
4.  For manual verification of historical audits, use:
    ```bash
    secret-scan --history --max-commits 10 --full
    ```

## 6. Risk Scoring and Filtering

With the introduction of the Advanced Risk Scoring System, findings are assigned a numeric risk score (0-100) and categorized into dynamic risk levels (CRITICAL, HIGH, MEDIUM, LOW).

1.  **Filtering Noise**: Use the `--min-score` flag to filter out low-confidence generic strings or test markers. For example, `--min-score 70` ensures only HIGH and CRITICAL findings are reported.
2.  **Strict Gating**: Combine `--min-score` with `--fail-on-risk CRITICAL` to strictly fail a CI build only when a very high-confidence secret (e.g., a verified structured pattern with proximity context) is found.
3.  **Natural Language Detection**: When scanning LLM prompts, the detector leverages a 100-character context window and fuzzy intent matching (e.g., "aquí está mi contraseña") to dramatically boost scores for contextual secrets and detect prompt leakage.

## 7. Scanning Large Repositories

When auditing repositories with thousands of commits or large file trees, use the scalability features:

1.  **Parallelization**: Use `--history` or `--input <dir>` to automatically trigger `ProcessPoolExecutor`. This distributes the workload across available CPU cores. Large individual files (>10MB) are automatically chunked and mapped into memory (`mmap`) to avoid memory exhaustion and garbage collector lag.
2.  **Caching**: The scanner maintains `.secretscan_cache`. Commits that have been scanned and found clean are skipped in subsequent runs, allowing for extremely fast incremental audits.
3.  **Fast Mode**: For rapid feedback (e.g., pre-commit hooks), use `--mode fast` to skip deep entropy analysis and non-essential rules.

## 8. Final Checks

* Run the demo script `./demo.sh` to verify real-world usage (force-scan, obfuscation, Git integration, highlighting, risk scoring).
* Confirm no secrets leaked in the commit (all test data is synthetic or base64-encoded).
* `git status` → `git add ...` → `git commit` → `git push`.

By following these steps you keep the pattern library healthy, the detection engine precise, and the project ready for production-grade releases.
