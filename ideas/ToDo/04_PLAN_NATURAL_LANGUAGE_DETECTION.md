# Task: Natural Language & Contextual Detection

## 1. Objective & Context
*   **Goal**: Improve detection accuracy in LLM prompts by understanding conversational context and intent markers.
*   **Rationale**: Secrets in LLM prompts are often preceded by specific human intent (e.g., "here is my key"). Traditional regex may miss these or fail to prioritize them.
*   **Files Affected**:
    *   `detector.py`: Update `SecretDetector` and `DetectionEngine`.
    *   `data/contextual/rules.json`: Add new intent-based rules.
    *   `report.py`: Update `Finding` to reflect context-based scoring.

## 2. Research & Strategy
*   **Pattern Analysis**: Use intent phrases like `(?i)(?:my|prod|our)\s+(?:api|token|secret|password|key)\s*[:=]` as triggers.
*   **Engine Choice**: RE2 for intent triggers; contextual proximity logic for scoring.
*   **Risk Tier**: Contextual.

## 3. Implementation Checklist
- [ ] **Intent Rules**: Add multi-lingual intent markers (English, French, Spanish, German) to `data/contextual/rules.json`.
- [ ] **Context Window**: Implement a 100-character sliding window in `SecretDetector._scan_block` to analyze text surrounding high-entropy strings.
- [ ] **Proximity Scoring**: Modify `DetectionEngine.calculate_confidence` to boost scores if an intent marker is within the context window.
- [ ] **Leakage Patterns**: Add rules for common prompt injection/leakage phrases (e.g., "Ignore all previous instructions").
- [ ] **Fuzzy Matching**: Integrate a lightweight fuzzy matching helper for intent markers (e.g., catching "psswrd").

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_context_window_logic`: Verify window correctly captures +/- 100 chars.
- [ ] `test_scoring_boost`: Assert `Finding.confidence` increases when an intent marker is nearby.
- [ ] `test_multilingual_intents`: Verify markers for all 4 languages trigger detection.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Conversational Secret Detection (e.g., "Here is my secret password: abc123random").
- [ ] **Scenario**: Spanish Context Detection (e.g., "Aquí está mi contraseña: abc123random").
- [ ] **Scenario**: Prompt Leakage Blocking.

### 4.3 Test Data Obfuscation
- [ ] Update `data/contextual/rules.json`.
- [ ] Run `python3 tools/generate_test_data.py`.
- [ ] Verify `test_data.json` contains obfuscated conversational examples.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Add "Natural Language Context" part showing boosted scores for conversational secrets.
- [ ] **`README.md`**: Document multi-lingual context support.
- [ ] **CLI Help**: Mention context-aware scanning in `--mode deep` description.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, high-signal.
*   **Perf**: Ensure context window analysis doesn't drop throughput below 15 MB/s.
*   **Security**: Always redact findings triggered by contextual rules.
