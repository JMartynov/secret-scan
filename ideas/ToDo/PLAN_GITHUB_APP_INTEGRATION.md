# Task: GitHub App Integration

## 1. Objective & Context
*   **Goal**: Build a GitHub App to provide automated PR scanning and commit blocking for repositories.
*   **Rationale**: Deep integration with the developer workflow is the primary growth channel and the core value proposition for engineering teams.
*   **Files Affected**:
    *   `app/api/github.py`: Webhook receiver and event handler.
    *   `app/services/github_service.py`: Logic for PR comments and Checks API updates.
    *   `git_engine.py`: Optimize for diff-based scanning.

## 2. Research & Strategy
*   **Mechanism**: Listen for `pull_request` and `check_suite` events via webhooks.
*   **Auth**: Secure JWT exchange for installation-specific access tokens.
*   **Engine Choice**: Linear-time RE2 scanning on PR diffs (additions only).

## 3. Implementation Checklist
- [ ] **Webhook Handler**: Implement logic to handle `opened`, `synchronize`, and `reopened` PR actions.
- [ ] **Surgical Diff Scanning**: Parse GitHub diffs to identify exact line numbers for additions, avoiding redundant scans of unchanged code.
- [ ] **PR Comments**: Implement automated, non-disruptive comments on lines where secrets are detected.
- [ ] **Checks API Integration**: Set "Pending", "Success", or "Failure" status on PRs based on the `fail-on-risk` policy.
- [ ] **Installation Flow**: Implement the OAuth2/App installation flow to manage repository permissions.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_diff_parsing`: Verify that the engine correctly identifies added lines from a standard git diff.
- [ ] `test_webhook_signature`: Ensure the app correctly validates incoming GitHub webhook signatures.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Leak in PR (Bot comments on the exact line and marks the Check as failed).
- [ ] **Scenario**: Clean PR (Check is marked as successful).
- [ ] **Scenario**: Partial Fix (Bot resolves previous comments when the secret is removed in a subsequent commit).

### 4.3 Test Data Obfuscation
- [ ] Use synthetic diffs in `tests/data/github_test_data.json`.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Show a simulated PR scan using a sample diff file.
- [ ] **`README.md`**: Add a "GitHub Integration" section with a "Connect to GitHub" button.
- [ ] **`docs/GITHUB_SETUP.md`**: Step-by-step guide for organizations to configure the app.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, high-signal.
*   **Perf**: Ensure PR scan results are delivered within 10 seconds of push.
*   **Security**: Never post the full raw secret in a PR comment; always use `redacted_value`.
