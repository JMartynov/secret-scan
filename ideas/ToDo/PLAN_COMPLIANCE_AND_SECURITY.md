# Task: Compliance & Security (SOC2 Readiness)

## 1. Objective & Context
*   **Goal**: Implement the technical controls and logging required for SOC2 compliance and enterprise security audits.
*   **Rationale**: To win enterprise contracts, the platform must demonstrate high standards of data protection and accountability.
*   **Files Affected**:
    *   `app/services/audit_logger.py` (Centralized logging)
    *   `app/core/security.py` (Encryption/Hashing)
    *   `infra/logging_config.yml` (Retention policies)

## 2. Research & Strategy
*   **Audit Logs**: Capture WHO did WHAT and WHEN (Logins, scans, rule changes).
*   **Encryption**: AES-256 for data at rest (DB) and TLS 1.3 for data in transit.
*   **Retention**: Implement 1-year log retention policy for audit trails.

## 3. Implementation Checklist
- [ ] **Audit Logging**: Create a dedicated service to log all sensitive actions to a non-volatile store.
- [ ] **SSO Integration**: Support SAML/OIDC (Okta, Azure AD) for enterprise logins.
- [ ] **Encryption at Rest**: Ensure all database volumes and S3 buckets are encrypted.
- [ ] **Vulnerability Scanning**: Integrate `snyk` or `trivy` into the CI/CD pipeline.
- [ ] **Incident Response**: Create automated alerts for anomalous activity (e.g., massive scan volume from one IP).
- [ ] **Data Deletion**: Implement a "Right to be Forgotten" (GDPR) endpoint to purge user data.

## 4. Testing & Verification (Mandatory)
### 4.1 Security Testing
- [ ] Run a penetration test on the API endpoints.
- [ ] Verify that audit logs cannot be modified by standard users.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Admin views the audit log and sees a detailed history of rule updates.
- [ ] **Scenario**: A login from a new, suspicious IP triggers a security alert.
- [ ] **Scenario**: Data is automatically purged after the 1-year retention period.

## 5. Demo & Documentation
- [ ] **Trust Center**: Create a public-facing page detailing security practices.
- [ ] **Audit Export**: Allow admins to export audit logs as CSV/JSON for their own compliance needs.

## 6. Engineering Standards
*   **Immutability**: Audit logs should ideally be stored in an append-only, immutable storage.
*   **Transparency**: Be clear with users about what data is collected and how it is protected.
