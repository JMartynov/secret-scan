# Task: Billing & Monetization System

## 1. Objective & Context
*   **Goal**: Integrate Stripe for usage-based billing and subscription management.
*   **Rationale**: To generate revenue and provide a sustainable commercial model for the SaaS platform.
*   **Files Affected**:
    *   `app/api/billing.py` (Stripe webhooks and endpoints)
    *   `app/services/billing_service.py` (Usage tracking)
    *   `frontend/pages/pricing.tsx` (Subscription UI)

## 2. Research & Strategy
*   **Provider**: Stripe (Subscriptions + Metered Billing).
*   **Tiers**: Free (1k scans), Pro ($29/mo), Team ($99/mo), Enterprise (Custom).
*   **Tracking**: Record scan volume in PostgreSQL/Redis and report to Stripe daily.

## 3. Implementation Checklist
- [ ] **Stripe Account Setup**: Configure products and price points in the Stripe dashboard.
- [ ] **Billing Portal**: Integrate Stripe Customer Portal for self-service management.
- [ ] **Usage Metering**: Implement logic to increment Stripe's usage meter on every successful scan.
- [ ] **Webhook Handler**: Handle `invoice.paid`, `customer.subscription.deleted`, and `checkout.session.completed` events.
- [ ] **Pricing Page**: Build a responsive pricing table in the Next.js frontend.
- [ ] **Feature Gating**: Implement middleware to block scans if a user exceeds their tier's limit.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test the webhook handler with mocked Stripe signatures.
- [ ] Verify usage reporting logic correctly handles API failures (retries).

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: User upgrades to Pro and their scan limit is instantly increased.
- [ ] **Scenario**: A user on the Free tier is blocked after 1,000 scans.
- [ ] **Scenario**: Payment failure results in the subscription being marked as "past_due".

## 5. Demo & Documentation
- [ ] **README.md**: Document the billing architecture and tier limits.
- [ ] **Dashboard UI**: Add a "Billing" tab showing current usage and invoice history.

## 6. Engineering Standards
*   **Compliance**: Ensure PCI-DSS compliance by never handling raw credit card data on our servers.
*   **Reliability**: Usage reporting must be idempotent to avoid double-charging.
