# Task: SaaS Backend API Service

## 1. Objective & Context
*   **Goal**: Build a production-grade FastAPI backend to provide secret scanning as a service.
*   **Rationale**: To transition from a CLI-only tool to a scalable SaaS platform with centralized management and multi-user support.
*   **Files Affected**:
    *   `app/main.py` (Entry point)
    *   `app/api/scan.py` (Scanning endpoints)
    *   `app/api/auth.py` (JWT Authentication)
    *   `app/models/` (DB Schemas: Users, Scans, Findings)
    *   `app/services/detector_service.py` (Engine wrapper)

## 2. Research & Strategy
*   **Tech Stack**: FastAPI (Async), PostgreSQL (SQLAlchemy/Tortoise), Redis (Rate limiting).
*   **Auth**: JWT-based authentication with organization-level scoping.
*   **Engine Choice**: Integration with existing `detector.py` and `obfuscator.py`.

## 3. Implementation Checklist
- [ ] **FastAPI Scaffolding**: Setup the project structure with dependency injection.
- [ ] **DB Schema Design**: Implement PostgreSQL tables for Users, Orgs, Scans, and Findings.
- [ ] **Auth Layer**: Implement login, register, and JWT verification middleware.
- [ ] **Scanning Endpoint**: Create `POST /scan` that accepts text/files and returns a risk report.
- [ ] **Streaming Support**: Implement `POST /scan-stream` for real-time log analysis.
- [ ] **Rate Limiting**: Integrate Redis to prevent API abuse.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test API endpoints using `httpx.AsyncClient`.
- [ ] Verify JWT token generation and validation.
- [ ] Test DB CRUD operations for scan history.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Authenticated user scans a secret and sees it in their history.
- [ ] **Scenario**: Unauthorized request is blocked by the auth middleware.
- [ ] **Scenario**: Rate limit is triggered after exceeding the configured threshold.

## 5. Demo & Documentation
- [ ] **API Documentation**: Ensure Swagger/OpenAPI docs are correctly generated at `/docs`.
- [ ] **README.md**: Add a "Server Mode" section with setup instructions.
- [ ] **Postman Collection**: Create a sample collection for testing the API.

## 6. Engineering Standards
*   **Perf**: Maintain sub-100ms latency for small text scans.
*   **Security**: Ensure secrets are NEVER stored in plain text in the database; only store metadata and redacted snippets.
