## Extended Infrastructure Mode — Status

1. **Pattern expansion**: migrated and reclassified rules across `api_keys`, `cloud_credentials`, `database_credentials`, `infrastructure`, `private_keys`, and `tokens`, following the PATTERN_LIBRARY_EXPANSION_2 plan.
2. **Detection refinements**: entropy-aware scoring, longest-match overlap resolution, and detection heuristics now follow the PLAN_CODE_HEALTH_AND_REFINEMENT guidelines, plus the CLI exposition of `--force-scan-all`.
3. **Demonstration & docs**: updated `demo.sh`, `README.md`, and `INSTRUCTIONS.md` to highlight synthetic obfuscation, force-scan coverage, and the developer tooling path (migrate → dedupe → lint → test).
4. **Tests**: acceptance coverage now includes the keywordless `Force-scan Keywordless Detection` scenario, and `pytest tests/test_acceptance.py::test_force_scan_keywordless` is part of the validation checklist.
