# Release Notes — Extended Infrastructure Mode

**Date:** 2026-03-26  
**Branch:** `feature/extended_infrastructure_mode`

## Summary

- Expanded the pattern library with a dedicated `infrastructure` taxonomy that now captures credit cards, IBANs, SSNs, national IDs, and other high-risk identifiers referenced in the PATTERN_LIBRARY_EXPANSION and PLAN_CODE_HEALTH documents.
- Hardened the detection engine with entropy-aware scoring, long-match deduplication, and the new `--force-scan-all` switch so logs without explicit keywords are still vetted.
- Documented the new workflow, updated the demo script, and refreshed the README/INSTRUCTIONS to reflect the synthetic/obfuscation tooling, CLI improvements, and developer utilities.

## Data & Detection

- Added or migrated `data/{api_keys,authentication,cloud_credentials,database_credentials,infrastructure,private_keys,tokens}` rules, including entropy defaults and normalized keywords, so every rule is compatible with the RE2 engine.
- Introduced the overlap-resolution heuristics described in PLAN_CODE_HEALTH_AND_REFINEMENT to ensure structured secrets displace generic entropy hits.
- Updated acceptance coverage with scenario 18 (`Force-scan Keywordless Detection`) to verify that `stripe_api_key` can be caught even when keywords are missing.
- Added synthetic obfuscation and hashed-mode demonstrations in `demo.sh`, plus new README and INSTRUCTIONS sections that highlight force-scan capabilities and developer tooling.

## Tooling

- `tools/migrate_patterns.py`, `tools/generate_test_data.py`, and `tools/deduplicate_rules.py` orchestrate normalization, sample regeneration, and duplicate removal for the refreshed taxonomy.
- `tools/regex_lint.py`, `tools/run_safe_regex.py`, and `tools/run_redoctor.py` continue to enforce code-health rules such as ReDoS resilience, schema compliance, and duplicate-free regex registration.
- The CLI now exposes `--force-scan-all` and improved obfuscation (`--obfuscate-mode synthetic`) for demo and automation workflows.

## Testing

- `pytest tests/test_acceptance.py::test_redaction`
- `pytest tests/test_acceptance.py::test_clustering`
- `pytest tests/test_acceptance.py::test_massive_validation`
- `pytest tests/test_acceptance.py::test_force_scan_keywordless`
- `pytest tests/test_detector.py`

The above tests have been executed locally to verify the critical acceptance scenarios, including the new keywordless mode. Additional suites (unit tests, library expansion, and CLI regression tests) remain available via `pytest tests/test_*.py`.
