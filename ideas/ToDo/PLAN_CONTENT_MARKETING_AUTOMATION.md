# Task: Content & Marketing Automation

## 1. Objective & Context
*   **Goal**: Build a system to automatically generate and publish security-related content based on anonymized leak data.
*   **Rationale**: To drive top-of-funnel traffic via SEO and social media presence (Twitter, Reddit, Substack).
*   **Files Affected**:
    *   `tools/content_gen.py` (AI content generation)
    *   `app/services/analytics_service.py` (Aggregated data)

## 2. Research & Strategy
*   **Platforms**: Reddit (r/programming), Twitter/X, Substack.
*   **Strategy**: "Data-Driven Security" — Share stats like "Top 10 most leaked keys of the week".
*   **AI**: Use LLMs to draft engaging, human-like posts from raw scan statistics.

## 3. Implementation Checklist
- [ ] **Stats Aggregator**: Query the DB for anonymized, high-level scanning trends.
- [ ] **AI Writer**: Integrate OpenAI/Anthropic to generate blog posts and social threads.
- [ ] **Reddit Bot**: Implement automated (but natural-looking) posting to relevant subreddits using PRAW.
- [ ] **Twitter Bot**: Setup automated posting of daily "Leak Alerts" or "Security Tips".
- [ ] **Substack Integration**: Generate drafts for weekly newsletters.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test the stats aggregation logic to ensure it doesn't include any PII.
- [ ] Verify that the AI prompt generates content in the correct tone and format.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: System generates a weekly summary of detected secrets and creates a draft post.
- [ ] **Scenario**: A "Security Tip" is posted to Twitter at the scheduled time.
- [ ] **Scenario**: The Reddit bot responds to a thread about "leaking secrets" with a helpful tip and link.

## 5. Demo & Documentation
- [ ] **Internal Dashboard**: Show content performance metrics (shares, views, referrals).
- [ ] **Policy**: Define strict guidelines to avoid "spammy" behavior and maintain brand reputation.

## 6. Engineering Standards
*   **Quality Over Quantity**: Focus on high-value, educational content rather than high-volume noise.
*   **Ethical Disclosure**: Never share enough data to identify specific victims or repositories.
