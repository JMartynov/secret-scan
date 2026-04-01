# Task: Automated Rule Intelligence & Updates

## 1. Objective & Context
*   **Goal**: Implement a system to automatically pull and update scanning rules from public and proprietary sources.
*   **Rationale**: The threat landscape changes rapidly; manual rule updates are insufficient for a production security tool.
*   **Files Affected**:
    *   `tools/rule_sync.py` (Sync logic)
    *   `data/rules.json` (Target for updates)
    *   `tools/migrate_patterns.py` (Normalization)

## 2. Research & Strategy
*   **Sources**: GitHub Public Secrets, Gitleaks, TruffleHog (Open source parts), and specialized security feeds.
*   **Normalization**: Use `migrate_patterns.py` to convert various formats into the project's RE2-compatible schema.
*   **Validation**: Every auto-updated rule MUST pass `tools/regex_lint.py` and `tools/run_regexploit.py`.

## 3. Implementation Checklist
- [ ] **Feed Aggregator**: Implement a script to fetch rule updates from configured Git repositories/APIs.
- [ ] **Automated Linting**: Integrate the linting suite into the sync process to block dangerous regex.
- [ ] **Versioned Rules**: Implement a versioning system for `rules.json` to allow rollbacks.
- [ ] **Dynamic Loading**: Update the `DetectionEngine` to support reloading rules without a restart.
- [ ] **Feedback Loop**: Implement a mechanism to mark rules as "noisy" or "false positive" to adjust thresholds automatically.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test the sync script with mocked external rule feeds.
- [ ] Verify that invalid regex from a feed is correctly identified and rejected.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: A new rule is added to a public source; the tool syncs and detects the new secret type within 24 hours.
- [ ] **Scenario**: A malicious/broken regex is pushed to a feed; the tool's linting blocks it from being deployed.
- [ ] **Scenario**: Admin rolls back the rule set to a previous version after a spike in false positives.

## 5. Demo & Documentation
- [ ] **README.md**: Add a section on "Rule Intelligence" and how to contribute new feeds.
- Task completion will be visible in the "Rule Management" section of the SaaS dashboard.

## 6. Engineering Standards
*   **Security**: Ensure rule feeds are fetched over HTTPS and verified (e.g., via GPG signatures or checksums).
*   **Safety**: Never auto-deploy rules to production without passing the automated security suite.
