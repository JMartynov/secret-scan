# Task: Growth & Outreach Bot (Autonomous Discovery)

## 1. Objective & Context
*   **Goal**: Build a bot to autonomously scan public GitHub repositories for leaks and notify owners via issues/PRs.
*   **Rationale**: Serves as an organic acquisition engine by providing immediate value to developers who have already leaked data.
*   **Files Affected**:
    *   `tools/outreach_bot.py`: Main bot logic and GitHub API client.
    *   `data/outreach_templates.json`: Multi-lingual, polite notification templates.

## 2. Research & Strategy
*   **Discovery**: Use GitHub Search API to find new commits matching high-risk keywords (e.g., `sk-`, `AKIA`).
*   **Safety**: Only notify on 100% verified secrets or extremely high-confidence matches.
*   **Policy**: Strictly follow GitHub's Anti-Spam and API guidelines.

## 3. Implementation Checklist
- [ ] **Search Engine**: Implement logic to crawl recent GitHub activity for common secret patterns.
- [ ] **Confidence Filter**: Add a strict gate that only allows "CRITICAL" risk findings to trigger an outreach event.
- [ ] **Deduplication Database**: Maintain a persistent store of notified repositories to avoid repeated alerts.
- [ ] **Polite Templates**: Draft non-alarmist, helpful issue templates that explain the risk and provide a link to the tool.
- [ ] **Analytics Tracking**: Add tracking parameters to links to measure conversion from "Issue" to "Tool Install".

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_search_query_builder`: Verify that search queries are optimized for high-yield results.
- [ ] `test_deduplication`: Assert that the bot never notifies the same repo twice.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Bot finds a clear leak (Drafts a high-quality issue report).
- [ ] **Scenario**: Bot hits rate limit (Gracefully pauses and schedules a resume).
- [ ] **Scenario**: Low-confidence match (Bot ignores and logs the finding).

### 4.3 Test Data Obfuscation
- [ ] **CRITICAL**: The bot must NEVER post raw secrets in public issues. Always redact.

## 5. Demo & Documentation
- [ ] **Internal Guide**: "Rules of Engagement" for the outreach bot.
- [ ] **Growth Dashboard**: Visual stats on issues opened vs. users acquired.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, helpful peer.
*   **Ethics**: The mission is "Help and Protect", not "Shame and Blame".
*   **Security**: Ensure the bot's own API keys are rigorously protected.
