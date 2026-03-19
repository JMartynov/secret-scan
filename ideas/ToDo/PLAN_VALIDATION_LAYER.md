# PLAN: Secret Validation Layer

## 1. Objective
Add an optional verification step to check if detected secrets are active, significantly reducing false positive noise for security teams.

## 2. Analogs & Research
- **TruffleHog (Verified)**: The gold standard for validation.
- **Gitleaks**: Added verification in recent versions via `--verify`.

## 3. Implementation Details

### 3.1 Architecture
- `validators/` directory containing modules for major providers:
    - `github.py`: Calls `/user` with the token.
    - `aws.py`: Calls `sts.get_caller_identity`.
    - `stripe.py`: Calls `/v1/account`.
- `ValidationManager`: Orchestrates calls, handles timeouts, and implements backoff.

### 3.2 Security Requirements
- **No Persistence**: Never store the secrets being verified.
- **Proxy Support**: Allow routing validation calls through a proxy for corporate environments.
- **User-Agent**: Use a custom User-Agent identifying the tool.
- **Minimal Scope**: Only request the most basic identity info to avoid triggering security alerts on the target account.

### 3.3 Workflow
1. Detector finds a match.
2. If `Finding.score > 60` and `--verify` is set:
    3. Pass to `ValidationManager`.
    4. Update `Finding.is_verified = True` if successful.
    5. Boost `Finding.score` to 100.

## 4. Best Practices
- **Rate Limiting**: Strictly respect provider rate limits to avoid getting the scanning IP blocked.
- **Caching**: Cache validation results (hashed) for the duration of the scan to avoid redundant network calls for duplicate secrets.
- **Parallelism**: Run validation calls in a thread pool as they are I/O bound.

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_validator_mock_api`**: Use `responses` or `unittest.mock` to simulate successful and failed (401, 403, 429) API calls for each provider.
- **`test_validation_manager_timeout`**: Ensure the manager correctly skips validation if the API doesn't respond within the configured timeout.
- **`test_backoff_logic`**: Verify that the manager waits between retries for 429 errors.
- **`test_validation_caching`**: Assert that `ValidationManager` only calls the external API once for identical secrets within a session.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Successful Verification Reporting**
  - Given a real GitHub token is detected (mocked API returns 200)
  - When I run the scan with `--verify`
  - Then the finding should be marked as "VERIFIED" and have a score of 100
- **Scenario: Invalid Secret Reporting**
  - Given an invalid Stripe key is detected (mocked API returns 401)
  - When I run the scan with `--verify`
  - Then the finding should NOT be marked as "VERIFIED"
- **Scenario: Handling Rate Limits**
  - Given the provider returns a "429 Too Many Requests"
  - When I run the scan
  - Then the tool should gracefully report the finding without verification status and continue.

---

## 6. Demo Update
Update `demo.sh` to include a section for "Secret Verification":
- Show how a verified secret is highlighted in the report.
- Use a mock verification mode to demonstrate the difference between a "Detected" and "Verified" secret.

---

## 7. Documentation Update
Update `README.md`:
- Add a section on "Secret Verification".
- Document the `--verify` flag and list supported providers (AWS, GitHub, Stripe).
- Include safety warnings about using verification in CI/CD environments.
