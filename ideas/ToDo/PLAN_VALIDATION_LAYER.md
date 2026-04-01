# Task: Secret Validation Layer

## 1. Objective & Context
*   **Goal**: Implement an optional verification step to check if detected secrets are live/active via external APIs.
*   **Rationale**: Eliminates false positives by confirming if a match is a real, functional credential.
*   **Files Affected**:
    *   `app/services/validation_manager.py`: New service to orchestrate checks.
    *   `app/validators/`: New directory for provider-specific logic (github, aws, stripe).
    *   `detector.py`: Hook into `SecretDetector` to trigger validation.
    *   `cli.py`: Add `--verify` flag.

## 2. Research & Strategy
*   **Mechanism**: Async HTTP calls to provider endpoints (e.g., GitHub `/user`, AWS `sts:GetCallerIdentity`).
*   **Security**: No-persistence policy for validated secrets; use hashing for caching.
*   **Engine Choice**: I/O-bound validation runs in a separate thread/process pool.

## 3. Implementation Checklist
- [ ] **Validator Base**: Create `validators/base.py` with the standard interface.
- [ ] **Provider Logic**: Implement initial validators for GitHub, AWS, and Stripe.
- [ ] **Validation Manager**: Implement `ValidationManager` with timeouts, backoff, and caching (hashed secrets).
- [ ] **Detector Hook**: Modify `SecretDetector` to pass high-confidence findings to the manager if `--verify` is set.
- [ ] **Status Reporting**: Update `report.py` to include a `VERIFIED` status in the output.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_validator_mocks`: Use `responses` to simulate API success/failure (401, 403, 429).
- [ ] `test_validation_cache`: Assert that identical secrets are only checked once per session.
- [ ] `test_validation_timeout`: Ensure slow APIs don't hang the scanner.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Successful Secret Verification (Marked as VERIFIED, Score boosted to 100).
- [ ] **Scenario**: Invalid Secret Reporting (No verification tag).
- [ ] **Scenario**: Rate Limit Handling (Graceful degradation).

### 4.3 Test Data Obfuscation
- [ ] **CRITICAL**: Never use real secrets for testing. Use mocked API responses and synthetic data.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Add a "Verified Secrets" part using a mock-verify mode.
- [ ] **`README.md`**: Document supported providers and security implications of `--verify`.
- [ ] **CLI Help**: Highlight that `--verify` requires network access.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, safety-conscious.
*   **Perf**: Validation is slow; ensure it doesn't block the main scanning loop.
*   **Security**: Strictly adhere to the "no persistence" rule for sensitive data during validation.
