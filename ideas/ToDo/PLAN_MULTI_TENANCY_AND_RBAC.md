# Task: Multi-Tenancy & RBAC Architecture

## 1. Objective & Context
*   **Goal**: Implement a multi-tenant architecture to support multiple organizations with isolated data and Role-Based Access Control (RBAC).
*   **Rationale**: Essential for enterprise customers who need to manage teams and restrict data access within their departments.
*   **Files Affected**:
    *   `app/db/base.py` (Row-level security logic)
    *   `app/api/orgs.py` (Management endpoints)
    *   `app/middleware/tenant.py` (Isolation enforcement)

## 2. Research & Strategy
*   **Isolation**: Row-level filtering based on `org_id` in all SQL queries.
*   **Roles**: `Owner` (Full access), `Admin` (Management), `Developer` (Scanning/Viewing), `Viewer` (ReadOnly).
*   **JWT**: Include `org_id` and `role` in the authentication token.

## 3. Implementation Checklist
- [ ] **Tenant Middleware**: Implement a middleware that extracts `org_id` from JWT and sets a context variable.
- [ ] **Base Repository**: Update the DB layer to automatically filter all queries by the current `org_id`.
- [ ] **Org Management**: Endpoints to create organizations, invite users, and manage roles.
- [ ] **RBAC Enforcement**: Implement decorators like `@requires_role('admin')` for sensitive endpoints.
- [ ] **Data Migration**: Update existing tables to include an `org_id` column.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Verify that a user from Org A cannot see data from Org B.
- [ ] Test that a 'Viewer' cannot delete a finding or update a rule.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Admin invites a new user to the organization with the 'Developer' role.
- [ ] **Scenario**: Cross-tenant data leak attempt is blocked by the database layer.
- [ ] **Scenario**: An organization is deleted, and all associated data is purged (or archived).

## 5. Demo & Documentation
- [ ] **README.md**: Document the multi-tenancy model and available roles.
- [ ] **Dashboard**: Add "Team Management" settings for admins.

## 6. Engineering Standards
*   **Strict Isolation**: Data isolation must be enforced at the lowest possible layer (DB queries).
*   **Auditability**: Every action in the organization should be logged with the user's identity.
