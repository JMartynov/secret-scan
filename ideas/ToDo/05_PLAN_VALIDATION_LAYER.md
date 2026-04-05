# Task: Secret Validation Layer

## 1. Objective & Context
*   **Goal**: Implement an optional verification step to check if detected secrets are live/active via external APIs.
*   **Rationale**: Eliminates false positives by confirming if a match is a real, functional credential. A "Verified" secret is a confirmed security incident, whereas a "Detected" secret is a potential one.
*   **Files Affected**:
    *   `src/validators/`: New directory for provider-specific logic (github, aws, stripe).
    *   `src/validation_manager.py`: New service to orchestrate checks.
    *   `detector.py`: Hook into `SecretDetector` to trigger validation.
    *   `cli.py`: Add `--verify` flag.
    *   `report.py`: Add `VERIFIED` status and visual markers.

## 2. Research & Strategy
*   **Mechanism**: Async HTTP calls to provider endpoints. Use the most "passive" check possible (e.g., identity checks rather than data access).
*   **Security**: 
    *   **No-persistence policy**: Secrets being verified are never written to disk or logs.
    *   **In-Memory Caching**: Use a SHA-256 hash of the secret as a cache key to avoid redundant network calls within a single scan session.
    *   **TLS Pinning**: (Optional) Ensure connections to providers are secure.
*   **Engine Choice**: Validation is I/O-bound. Use a `ThreadPoolExecutor` or `asyncio` to avoid blocking the regex scanning engine.

## 3. Technical Specifications: Provider Endpoints
| Provider | Validation Endpoint | Success Indicator | Passive/Safe? |
| :--- | :--- | :--- | :--- |
| **GitHub** | `GET https://api.github.com/user` | `200 OK` (Valid Token) | Yes (Identity Only) |
| **AWS** | `POST https://sts.amazonaws.com/` | `Action=GetCallerIdentity` (Valid pair) | Yes (Identity Only) |
| **Stripe** | `GET https://api.stripe.com/v1/accounts` | `200 OK` | Yes (Metadata) |
| **Slack** | `POST https://slack.com/api/auth.test` | `{"ok": true}` | Yes |
| **Google Cloud**| `GET https://www.googleapis.com/oauth2/v1/tokeninfo` | `200 OK` | Yes |

## 4. Implementation Checklist
- [ ] **Validator Base**: Create `src/validators/base.py` with an abstract `Validator` class.
- [ ] **Provider Implementation**:
    - [ ] `GitHubValidator`: Check `Authorization: token <key>`.
    - [ ] `AWSValidator`: Sign requests for `sts:GetCallerIdentity`.
    - [ ] `StripeValidator`: Check `Authorization: Bearer <key>`.
- [ ] **Validation Manager**:
    - [ ] Implement rate-limit handling (Exponential Backoff).
    - [ ] Implement a circuit breaker to stop verification if the provider is down or throttling heavily.
    - [ ] Implement the `SecretCache` (Memory-only, Hash-based).
- [ ] **Detector Integration**:
    - [ ] Update `Finding` dataclass to include `is_verified` (bool).
    - [ ] Add `SecretDetector.verify_findings(findings)` method.
- [ ] **Scoring Escalation**:
    - [ ] If `is_verified == True`, boost `risk_score` to **100** and set `severity` to **CRITICAL**.

## 5. Related Concepts
### 5.1 Canary Tokens (Honeypots)
*   **Concept**: Some organizations intentionally place "fake" secrets (Canary Tokens) in code. If these are "verified," the provider alerts the security team that a breach or scan is in progress.
*   **Implementation**: The validation layer should check if the metadata returned by the provider identifies the key as a "Canary" or "Internal Research" key and flag it differently in the report.

### 5.2 Severity Escalation vs. Remediation
*   **Unverified Match**: Suggest rotation as a precaution.
*   **Verified Match**: Mandatory immediate revocation. The report should provide a direct "Revocation URL" for the provider.

### 5.3 False Positive Suppression (The "Example" problem)
*   Verification effectively solves the issue where strings like `AKIAEXAMPLE123456789` trigger a high-entropy match but are clearly invalid.

## 6. Testing & Verification (Mandatory)
### 6.1 Unit Testing
- [ ] `test_validator_mocks`: Use `responses` or `httpretty` to simulate API success/failure (401, 403, 429).
- [ ] `test_validation_cache`: Assert that identical secrets are only checked once.
- [ ] `test_validation_timeout`: Ensure slow APIs (latency > 2s) are aborted.

### 6.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Successful Secret Verification (Marked as VERIFIED, Score boosted to 100).
- [ ] **Scenario**: Rate Limit Handling (Engine waits or skips remaining verifications).

## 7. Demo & Documentation
- [ ] **`demo.sh`**: Add a `--verify` demonstration using a local mock server.
- [ ] **`README.md`**: Add a "Verification Matrix" showing which providers are supported.
- [ ] **CLI Help**: Add a warning: `--verify sends matches to external APIs. Use with caution in air-gapped environments.`

## 8. Engineering Standards
*   **Isolation**: Validation logic must reside in `src/validators/` to keep `detector.py` focused on detection.
*   **Network Safety**: Use `requests.Session` with a reasonable timeout (max 3 seconds).
*   **Privacy**: NEVER log the full secret, even if it is verified.
