# Task: Growth & Outreach Bot (Autonomous Discovery)

## 1. Objective & Context
*   **Goal**: Build a bot to autonomously scan public GitHub repositories for leaks and notify owners.
*   **Rationale**: This serves as a powerful organic acquisition engine by showing direct value to potential users.
*   **Files Affected**:
    *   `tools/outreach_bot.py` (Bot logic)
    *   `data/outreach_templates.json` (Message variants)

## 2. Research & Strategy
*   **Discovery**: Use GitHub Search API to find new commits/repos matching high-risk keywords.
*   **Action**: Create a GitHub Issue or PR comment with a polite warning and a link to the tool.
*   **Compliance**: Strictly follow GitHub's API rate limits and Terms of Service to avoid being flagged as spam.

## 3. Implementation Checklist
- [ ] **Search Engine**: Implement logic to find repos using queries like `openai api_key` or `db_password`.
- [ ] **Confidence Filter**: Only act on "CRITICAL" (Verified) or "HIGH" confidence findings.
- [ ] **Deduplication**: Ensure the bot never notifies the same repository twice for the same leak.
- [ ] **Issue Generator**: Create personalized, non-alarmist issue templates.
- [ ] **Analytics**: Track "Click-through Rate" from GitHub issues to the landing page.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test the search query builder with various keyword combinations.
- [ ] Verify deduplication logic using a mock database.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Bot finds a public repo with a clear leak and generates a draft issue.
- [ ] **Scenario**: Bot skips a repository it has already processed.
- [ ] **Scenario**: Bot pauses execution after reaching the GitHub API rate limit.

## 5. Demo & Documentation
- [ ] **Internal Guide**: Document the bot's operating parameters and "Rules of Engagement".
- [ ] **Dashboard**: Add a "Growth Stats" section showing bot activity and conversions.

## 6. Engineering Standards
*   **Ethics**: The goal is to help, not to shame. Use professional, helpful language.
*   **Safety**: Never post the actual secret in the public issue; refer to the line number and redacted version.
