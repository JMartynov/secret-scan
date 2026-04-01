# Task: Multi-Tenancy & RBAC Architecture

## 1. Objective & Context
*   **Goal**: Implement a multi-tenant architecture with Role-Based Access Control (RBAC) to support enterprise teams.
*   **Rationale**: Essential for corporate security teams who need to manage multiple departments, restrict data access, and maintain an audit trail.
*   **Files Affected**:
    *   `app/models/`: Add `Organization`, `Member`, and `Role` models.
    *   `app/middleware/auth.py`: Update to enforce org-level isolation.
    *   `app/api/admin.py`: Management endpoints for organizations and members.

## 2. Research & Strategy
*   **Mechanism**: Every database record (Scan, Finding, Rule) is tagged with an `organization_id`.
*   **Roles**: `Owner`, `Admin`, `Developer`, `Viewer`.
*   **Isolation**: Strict row-level security enforced at the repository/ORMLayer.

## 3. Implementation Checklist
- [ ] **Org Models**: Implement SQLModel/Tortoise schemas for Organizations and Memberships.
- [ ] **Tenant Isolation Middleware**: Implement a middleware that extracts `org_id` from the JWT and injects it into the DB session.
- [ ] **RBAC Decorators**: Create `@requires_role` decorators to protect administrative and write-access endpoints.
- [ ] **Invitation System**: Build a secure flow for inviting new team members via email.
- [ ] **Audit Logging**: Implement a "System Audit Log" that records all role changes and administrative actions per organization.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_tenant_leakage`: Assert that User A from Org 1 cannot see findings from Org 2.
- [ ] `test_role_permissions`: Verify that a 'Viewer' cannot delete a scan or update a rule.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Team Onboarding (Owner invites Admin, Admin invites Developer).
- [ ] **Scenario**: Cross-Tenant Access Attempt (System blocks unauthorized data access).
- [ ] **Scenario**: Role Upgrade (User is granted Admin rights and gains access to settings).

### 4.3 Test Data Obfuscation
- [ ] Use synthetic UUIDs for all tenant and user IDs.

## 5. Demo & Documentation
- [ ] **`README.md`**: Document the multi-tenant security model.
- [ ] **API Docs**: Update Swagger to reflect role requirements for each endpoint.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, security-focused.
*   **Perf**: Database indexes must be optimized for `(organization_id, created_at)` to ensure fast tenant-specific queries.
*   **Security**: Org isolation is the highest priority; one failure here is a critical security breach.
