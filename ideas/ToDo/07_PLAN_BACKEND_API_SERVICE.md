# Task: SaaS Backend API Service

## 1. Objective & Context
*   **Goal**: Build a production-grade FastAPI backend to provide secret scanning as a service.
*   **Rationale**: Transitions from a CLI-only tool to a scalable SaaS platform with centralized management.
*   **Files Affected**:
    *   `app/main.py`: API Entry point.
    *   `app/api/scan.py`: Scanning endpoints (`/scan`, `/scan-stream`).
    *   `app/services/detector_service.py`: Wrapper for `SecretDetector`.
    *   `app/models/`: SQLModel/Tortoise definitions for `ScanResult` and `Organization`.

## 2. Research & Strategy
*   **Stack**: FastAPI (Async), PostgreSQL (SQLModel), Redis (Rate Limiting).
*   **Logic**: Expose core `detector.py` functionality via a RESTful API.
*   **Auth**: JWT-based authentication with per-organization scoping.

## 3. Implementation Checklist
- [ ] **FastAPI Setup**: Implement basic project structure with `pydantic` schemas for request/response.
- [ ] **Engine Integration**: Create a thread-safe `DetectorService` that manages a pool of `SecretDetector` instances.
- [ ] **Async Streaming**: Implement a streaming endpoint that accepts `multipart/form-data` and yields results as they are found.
- [ ] **Scan History**: Implement PostgreSQL storage for anonymized scan metadata (time, file count, severity counts).
- [ ] **Rate Limiting**: Integrate `fastapi-limiter` with Redis to prevent API abuse.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_scan_endpoint`: Verify JSON responses match the `Finding` schema.
- [ ] `test_auth_middleware`: Assert that invalid tokens are rejected.
- [ ] `test_concurrent_scans`: Verify API remains responsive under multiple simultaneous requests.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Authenticated user scans a secret and it appears in their scan history.
- [ ] **Scenario**: Unauthorized request is blocked.
- [ ] **Scenario**: Rate limit is triggered after exceeding the tier threshold.

### 4.3 Test Data Obfuscation
- [ ] Ensure API responses in tests use `redacted_value` by default.

## 5. Demo & Documentation
- [ ] **OpenAPI**: Ensure `/docs` (Swagger) is fully documented with request/response examples.
- [ ] **Postman Collection**: Create a collection for easy onboarding of external developers.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, high-signal.
*   **Perf**: Target < 100ms latency for small text scans (excluding network).
*   **Security**: Strictly enforce SSL/TLS; never log the `text` field of incoming scan requests.
