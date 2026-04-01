# Task: Billing & Monetization System

## 1. Objective & Context
*   **Goal**: Integrate Stripe for usage-based billing and subscription management.
*   **Rationale**: Ensures the project has a sustainable commercial model and allows users to pay for increased scan limits and premium features.
*   **Files Affected**:
    *   `app/api/billing.py`: Webhook handler and subscription endpoints.
    *   `app/services/usage_service.py`: Logic for tracking scan volume and reporting to Stripe.
    *   `frontend/pages/billing.tsx`: Billing management UI.

## 2. Research & Strategy
*   **Provider**: Stripe (Subscriptions + Metered Billing).
*   **Logic**: Associate every Organization with a Stripe Customer; track scans as usage events.
*   **Pricing**: Free (1k scans), Pro ($29/mo), Team ($99/mo), Enterprise (Metered).

## 3. Implementation Checklist
- [ ] **Stripe Account Setup**: Define products, prices, and tax rules in the Stripe Dashboard.
- [ ] **Checkout Integration**: Implement Stripe Checkout for seamless subscription onboarding.
- [ ] **Usage Metering**: Add logic to `detector_service.py` to record a usage event for every successful scan.
- [ ] **Webhook Processor**: Handle `invoice.paid`, `customer.subscription.deleted`, and `checkout.session.completed` events.
- [ ] **Tier Enforcement**: Implement middleware that blocks scans if the organization has exceeded its quota or has a failed payment status.
- [ ] **Billing Portal**: Integrate Stripe Customer Portal for managing payment methods and invoices.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_usage_reporting`: Verify that scan counts are correctly totaled and sent to Stripe.
- [ ] `test_webhook_signature`: Assert that only valid Stripe webhooks are processed.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: User upgrades to Pro (Quota is instantly increased).
- [ ] **Scenario**: Payment Fails (Access to deep scanning is restricted).
- [ ] **Scenario**: Usage Limit Reached (System prevents further scans and prompts for an upgrade).

### 4.3 Test Data Obfuscation
- [ ] Use standard Stripe Test Cards and synthetic customer IDs.

## 5. Demo & Documentation
- [ ] **Pricing Page**: Build a clear pricing table in the frontend.
- [ ] **README.md**: Document the available plans and limits.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, business-aligned.
*   **Perf**: Usage tracking must be asynchronous to avoid slowing down the scanning process.
*   **Security**: Never store credit card data; strictly use Stripe's secure tokens and hosted elements.
