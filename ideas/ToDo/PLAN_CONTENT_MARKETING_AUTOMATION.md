# Task: Content & Marketing Automation

## 1. Objective & Context
*   **Goal**: Build a system to automatically generate and publish security-related content based on anonymized leak trends.
*   **Rationale**: Drives top-of-funnel traffic through authority and data-driven security insights on social platforms.
*   **Files Affected**:
    *   `tools/content_gen.py`: AI-powered post generator.
    *   `app/services/analytics_service.py`: Aggregator for anonymized scan data.

## 2. Research & Strategy
*   **Platforms**: Reddit (r/programming), Twitter/X, Substack.
*   **Logic**: Aggregated Stats -> LLM (GPT-4/Claude) -> Formatted Posts.
*   **Content Types**: "Daily Leak Report", "Top 5 AI Security Risks", "Case Study: How to Secure Prompts".

## 3. Implementation Checklist
- [ ] **Stats Aggregator**: Implement a service that pulls anonymized counts of secret types found per day.
- [ ] **Post Generator**: Connect to an LLM API to transform raw stats into engaging, human-like narratives.
- [ ] **Social Media Client**: Implement basic clients for Twitter and Reddit (via PRAW) for automated posting.
- [ ] **Human-in-the-Loop**: Create a simple "Approval Dashboard" where a human must click "Publish" on generated content.
- [ ] **Engagement Tracking**: Track likes/shares/referrals for each piece of content.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_anonymization`: Assert that NO PII or raw secrets are ever included in the content generation prompt.
- [ ] `test_llm_prompt_integrity`: Verify the generator stays on-topic and follows the brand voice.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Weekly Summary (System generates a high-quality Substack draft from last week's data).
- [ ] **Scenario**: Trending Alert (System identifies a spike in a specific leak type and drafts a Twitter thread).
- [ ] **Scenario**: Referral Success (Content includes links that are correctly tracked in the dashboard).

### 4.3 Test Data Obfuscation
- [ ] All marketing examples must use placeholder secrets.

## 5. Demo & Documentation
- [ ] **Content Calendar**: Document the automated posting schedule.
- [ ] **Brand Guidelines**: Define the tone and voice for the AI writer.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, authoritative yet accessible.
*   **Ethics**: Never sensationalize leaks; focus on education and prevention.
*   **Security**: Anonymization must be multi-layered and verified by code reviews.
