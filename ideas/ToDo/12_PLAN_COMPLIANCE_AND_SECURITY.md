# Task: Compliance & Security (SOC2 Readiness)

## 1. Objective & Context
*   **Goal**: Implement technical controls and logging required for SOC2 Type II compliance and enterprise audits.
*   **Rationale**: Mandatory for selling into regulated industries and large enterprises that require formal proof of security.
*   **Files Affected**:
    *   `app/services/audit_logger.py`: Centralized security event logging.
    *   `app/core/security.py`: Strengthened encryption and hashing algorithms.
    *   `infra/logging_config.yml`: Log retention and SIEM integration.

## 2. Research & Strategy
*   **Controls**: Access control, data encryption at rest/transit, audit logging, and vulnerability management.
*   **Encryption**: Upgrade to AES-256-GCM for all sensitive data volumes.
*   **Audit Trail**: Capture Who, What, When, Where for all security-relevant events.

## 3. Implementation Checklist
- [ ] **Centralized Audit Log**: Implement a tamper-evident audit logging service that records all logins, configuration changes, and scan executions.
- [ ] **Data Encryption**: Ensure all database backups and S3 buckets are encrypted with customer-managed keys (CMK) if required.
- [ ] **Vulnerability Scanning**: Automate `snyk` and `trivy` scans in the CI/CD pipeline and block builds with critical vulnerabilities.
- [ ] **Session Management**: Implement strict session timeouts and concurrent session limits.
- [ ] **Disaster Recovery**: Define and automate the RTO/RPO policies and regular restore tests.

## 4. Testing & Verification (Mandatory)
### 4.1 Security Testing
- [ ] `test_audit_trail_integrity`: Verify that audit logs contain all required compliance fields.
- [ ] `test_encryption_at_rest`: Assert that raw data is unreadable in the database storage layer.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Access Review (Admin generates a report of all user access and role changes for the last quarter).
- [ ] **Scenario**: Incident Detection (Alert is triggered after 5 failed login attempts from the same IP).
- [ ] **Scenario**: Data Purge (Verify that "Right to be Forgotten" requests result in a complete purge of user data).

### 4.3 Test Data Obfuscation
- [ ] All audit logs must redact the secrets that triggered the findings.

## 5. Demo & Documentation
- [ ] **Trust Center**: Create a public-facing page detailing technical security controls.
- [ ] **Compliance Report**: Build a feature for admins to export an "Audit Pack" for their compliance officers.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, compliance-aware.
*   **Perf**: Logging must be non-blocking.
*   **Security**: SOC2 is a continuous process; ensure all controls are automated and self-healing.
