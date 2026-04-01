# Task: Automated Rule Intelligence & Updates

## 1. Objective & Context
*   **Goal**: Implement a system to automatically pull, normalize, and update scanning rules from public and proprietary feeds.
*   **Rationale**: Keeps the detection engine effective against new secret formats without requiring manual intervention from the core team.
*   **Files Affected**:
    *   `tools/rule_sync.py`: Logic for fetching and syncing rules.
    *   `tools/migrate_patterns.py`: Normalization helper.
    *   `data/`: Rule target directories.

## 2. Research & Strategy
*   **Sources**: GitHub Public Secrets, Gitleaks, and proprietary security intelligence feeds.
*   **Normalization**: Convert all patterns to RE2-compatible regex and assign default metadata (Risk, Confidence).
*   **Safety**: All updated rules must pass the internal linting and ReDoS protection suite.

## 3. Implementation Checklist
- [ ] **Rule Fetcher**: Implement a service to monitor and pull updates from configured rule repositories.
- [ ] **Pattern Normalizer**: Refine `migrate_patterns.py` to handle advanced regex features (like lookaheads) by converting them to safe RE2 equivalents where possible.
- [ ] **Automated CI for Rules**: Setup a GitHub Action that runs `tools/regex_lint.py` and `tools/run_regexploit.py` on every rule update.
- [ ] **Staging Layer**: Implement a "Rule Staging" process where new rules are tested against a baseline before being promoted to the "Stable" rule-set.
- [ ] **Dynamic Engine Reload**: Modify `DetectionEngine` to reload rules from disk without requiring a process restart.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_rule_normalization`: Verify that complex patterns are correctly converted to the internal schema.
- [ ] `test_lint_rejection`: Assert that a rule with a known ReDoS vulnerability is blocked from syncing.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: New Rule Sync (Tool automatically picks up a new pattern for a recently launched cloud provider).
- [ ] **Scenario**: Safe Rollback (Admin reverts to a previous rule-set after a new rule causes excessive false positives).
- [ ] **Scenario**: Hot Reload (Rules are updated while a long-running scan is in progress).

### 4.3 Test Data Obfuscation
- [ ] Auto-generate matching test data for new rules using `tools/generate_test_data.py`.

## 5. Demo & Documentation
- [ ] **README.md**: Document the "Rule Intelligence" sources and sync frequency.
- [ ] **Dashboard**: Show a "Last Rule Update" timestamp and a changelog of new detection patterns.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, high-signal.
*   **Perf**: Sync should be lightweight and run during off-peak hours.
*   **Security**: Verify the integrity of rule feeds using GPG signatures or checksums.
