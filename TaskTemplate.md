# Task Template: Secret Scan Feature Enhancement

Use this template when planning and implementing new features or rules for the `secret-scan` tool.

## 1. Objective & Context
*   **Goal**: [Clear, one-sentence description of the feature]
*   **Rationale**: [Why is this needed? e.g., "Improve detection of MongoDB SRV records in LLM prompts"]
*   **Files Affected**:
    *   `detector.py` (Engine logic)
    *   `report.py` (Formatting/Findings)
    *   `data/rules.json` (Patterns)
    *   `cli.py` (User interface)

## 2. Research & Strategy
*   **Pattern Analysis**: [If adding a rule, provide regex and example matches]
*   **Engine Choice**: [RE2 for safety, Aho-Corasick for speed, or Contextual rules]
*   **Risk Tier**: [Structured / Infrastructure / Contextual / Entropy / PII]

## 3. Implementation Checklist
- [ ] **Surgical Edits**: Use `replace` for targeted updates to existing classes (`SecretDetector`, `DetectionEngine`).
- [ ] **Keyword Filtering**: Ensure every new rule has high-signal keywords for pre-filtering.
- [ ] **ReDoS Protection**: Avoid nested quantifiers; verify with `tools/run_regexploit.py`.
- [ ] **Streaming Integrity**: If modifying chunking, verify `overlap` buffer handling (4096-char default).

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Add new cases to `tests/test_detector.py` or `tests/test_report.py`.
- [ ] Ensure 100% pass rate: `pytest tests/test_detector.py`.

### 4.2 Acceptance Testing (BDD)
- [ ] Add a new `Scenario` to `tests/acceptance.feature`.
- [ ] Implement step definitions in `tests/test_acceptance.py`.
- [ ] Verify: `pytest tests/test_acceptance.py`.

### 4.3 Test Data Obfuscation
- [ ] Update `data/rules.json`.
- [ ] Run `python3 tools/generate_test_data.py` to rebuild `data/test_data.json`.
- [ ] **Security**: Verify samples in `test_data.json` use `DUMMY_IGNORE` or are obfuscated to pass GitHub Push Protection (GH013).

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Add a new "Part X" to the script demonstrating the feature in a realistic pipe/stream.
- [ ] **`README.md`**: Update "Secret Types Detected", "Usage", or "Roadmap" sections.
- [ ] **CLI Help**: If adding a flag, verify it appears in `python3 cli.py --help`.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, direct, high-signal.
*   **Perf**: Maintain 10-20 MB/s scanning throughput.
*   **Security**: Never log or print raw detected secrets; always use `Finding.redacted_value`.
