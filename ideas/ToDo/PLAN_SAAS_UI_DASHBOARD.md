# Task: SaaS UI Dashboard

## 1. Objective & Context
*   **Goal**: Create a modern, high-performance web dashboard for managing secret scans and organization security.
*   **Rationale**: Users need a visual interface to track leaks, manage team access, and view security trends across their projects.
*   **Files Affected**:
    *   `frontend/` (New Next.js project)
    *   `frontend/pages/dashboard.tsx` (Overview)
    *   `frontend/components/ScanTable.tsx` (Finding list)
    *   `frontend/components/RiskChart.tsx` (Analytics)

## 2. Research & Strategy
*   **Tech Stack**: Next.js (App Router), Tailwind CSS, shadcn/ui, Recharts.
*   **Style**: Minimalist, high-contrast, "Linear-style" UI.
*   **Interactions**: Real-time updates via WebSockets or polling for active scans.

## 3. Implementation Checklist
- [ ] **Frontend Scaffolding**: Initialize Next.js with TypeScript and Tailwind.
- [ ] **Auth Integration**: Connect to Backend API JWT auth.
- [ ] **Overview Page**: Implement metrics for Total Scans, Secrets Found, and Risk Score.
- [ ] **Findings Explorer**: Create a searchable/filterable table of detected leaks.
- [ ] **Analytics Dashboard**: Implement charts showing secret leak trends over time.
- [ ] **Settings Page**: UI for managing API keys and organization members.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test UI components with Jest and React Testing Library.
- [ ] Verify data fetching and error handling states.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: User logs in and sees their scan history chart.
- [ ] **Scenario**: User filters findings by "CRITICAL" severity.
- [ ] **Scenario**: Real-time scan updates the dashboard without a page refresh.

## 5. Demo & Documentation
- [ ] **Component Library**: Document custom UI components.
- [ ] **Deployment**: Setup Vercel or Netlify for automated frontend deployments.

## 6. Engineering Standards
*   **Tone**: Polished, professional, and developer-friendly.
*   **Aesthetics**: Ensure consistent spacing, typography, and interactive feedback.
*   **Security**: Implement CSRF protection and ensure no raw secrets are ever exposed to the client-side state.
