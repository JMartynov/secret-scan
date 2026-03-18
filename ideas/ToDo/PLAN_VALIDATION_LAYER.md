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
