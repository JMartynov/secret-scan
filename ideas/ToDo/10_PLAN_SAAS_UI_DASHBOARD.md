# Task: SaaS UI Dashboard

## 1. Objective & Context
*   **Goal**: Create a modern, high-performance web dashboard for managing secret scans and security policies.
*   **Rationale**: Provides a visual interface for security admins to monitor trends, review findings, and manage team access.
*   **Files Affected**:
    *   `frontend/`: New Next.js project.
    *   `frontend/components/findings/`: Reusable finding components.
    *   `frontend/services/api.ts`: API client for the Backend service.

## 2. Research & Strategy
*   **Stack**: Next.js (App Router), Tailwind CSS, shadcn/ui, Recharts.
*   **Design**: Minimalist "Security Dashboard" aesthetic (Linear-style).
*   **Interaction**: Real-time finding alerts via WebSockets or SSE.

## 3. Implementation Checklist
- [ ] **Frontend Scaffold**: Initialize Next.js with TypeScript and Tailwind.
- [ ] **Dashboard Overview**: Implement high-level metrics (Scans, Leaks, Risk Score) with interactive charts.
- [ ] **Finding Explorer**: Build a filterable/searchable table of all detected leaks across the organization.
- [ ] **Policy Editor**: Create a UI for toggling rules and adjusting sensitivity thresholds.
- [ ] **Auth Flow**: Implement Login/SSO integration and persistent session management.
- [ ] **Team Management**: UI for inviting members and assigning roles (RBAC).

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_findings_table`: Assert correct filtering of severity levels.
- [ ] `test_risk_chart`: Verify chart rendering with various data points.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Admin filters findings to show only "HIGH" risk items from the last 24 hours.
- [ ] **Scenario**: User toggles a rule off in the dashboard and confirms it's reflected in API scans.
- [ ] **Scenario**: Real-time notification appears when a new leak is detected via a background CI job.

## 5. Demo & Documentation
- [ ] **Product Tour**: Create a "Quick Tour" onboarding for new users.
- [ ] **Storybook**: (Optional) Implement Storybook for UI component consistency.

## 6. Engineering Standards
*   **Aesthetics**: Ensure consistent spacing, polished typography, and interactive hover states.
*   **Accessibility**: Maintain WCAG compliance for dashboard accessibility.
*   **Security**: Implement strict Content Security Policy (CSP) and CSRF protection.
