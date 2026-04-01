# Task: GitHub App Integration

## 1. Objective & Context
*   **Goal**: Build a GitHub App to provide automated PR scanning and commit blocking.
*   **Rationale**: Deep integration with GitHub is the primary growth channel and core workflow for enterprise users.
*   **Files Affected**:
    *   `app/api/github.py` (Webhook handler)
    *   `app/services/github_service.py` (API interactions)
    *   `manifest.yml` (App permissions)

## 2. Research & Strategy
*   **Mechanics**: Webhooks for `pull_request` and `push` events.
*   **Feedback**: Post comments on PRs and set Status Checks (Checks API).
*   **Security**: Use App Private Keys and JWT for installation token exchange.

## 3. Implementation Checklist
- [ ] **Webhook Receiver**: Handle `pull_request` and `check_suite` events.
- [ ] **Diff Scanning**: Efficiently scan only the changed lines in a PR diff.
- [ ] **PR Comments**: Implement automated commenting on lines where secrets are found.
- [ ] **Checks API**: Set "Pending/Success/Failure" status on commits based on scan results.
- [ ] **Installation Flow**: Handle new app installations and organization setup.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Mock GitHub API responses for token exchange and commenting.
- [ ] Test diff parsing and range calculation for comments.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: User opens a PR with a secret, and the bot comments on the exact line.
- [ ] **Scenario**: A "clean" PR passes the security check status.
- [ ] **Scenario**: Merging is blocked if a secret is detected (configured in repo settings).

## 5. Demo & Documentation
- [ ] **README.md**: Add "GitHub Integration" setup guide.
- [ ] **Landing Page**: Show "Verified by GitHub" badge and screenshots of PR comments.

## 6. Engineering Standards
*   **Security**: Never store GitHub private keys in the repo; use environment variables or a Secret Manager.
*   **Reliability**: Implement webhook retries and idempotency.
