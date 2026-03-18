Feature: Comprehensive Secret Detection Acceptance
  As a security engineer
  I want to validate the secret detector against all performance and safety design rules
  So that I can ensure robust leak prevention without system instability.

  Background:
    Given the detector is initialized with standard settings

  Scenario: 1. Basic Pattern Matching (RE2 Engine)
    When I scan the text "stripe key is sk_live_PLACEHOLDER_51IyGfSAdFvX8EZYbATS56oaKOXwIizD05otbS42rQ0Q7ND"
    Then it should find "stripe_api_key"
    And the report should be redacted

  Scenario: 2. Conversational Context Detection
    When I scan the text "Here is our prod database password: random_string_123_abc"
    Then it should find a "Contextual Secret (LLM Prompt)"

  Scenario: 3. High-Entropy Validation
    When I scan a standalone hash "d8c7b92f4a19c70f7eaf8dbfa98e91c3"
    Then it should find "High Entropy String"
    When I scan "My secret key is d8c7b92f4a19c70f7eaf8dbfa98e91c3"
    Then it should find "Potential Secret (High Entropy + Context)"

  Scenario: 4. Keyword Filtering Efficiency
    When I scan a text matching a regex but missing its keyword
    Then the specific rule should NOT be triggered

  Scenario: 5. Input Safety - Large Input Truncation
    Given a massive input of 150000 characters
    When I run the scan
    Then findings beyond 100000 characters should be ignored

  Scenario: 6. ReDoS Safety - Signal Timeouts
    Given a ReDoS-prone string "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
    When I run the scan
    Then the engine should return within 2 seconds
    And it should not hang

  Scenario: 7. Privacy and Redaction
    When I scan "my key is ghp_1234567890abcdefghijklmnopqrstuvwx"
    Then the report content for "github_token" must be redacted like "ghp_...uvwx"

  Scenario: 8. Multi-Type Secret Clustering
    Given a file containing a Stripe key, a Github token, and a Contextual secret
    When I run the scan
    Then it should report all 3 distinct secrets

  Scenario: 9. Line Number Integrity
    Given a 100-line file with a secret on line 50
    When I run the scan
    Then the finding location must be "line 50"

  Scenario: 10. Deduplication of Overlapping Rules
    When I scan a string that matches multiple rules
    Then the final report should deduplicate findings for the same location

  Scenario: 11. Multi-Line Secret Detection
    Given a secret that spans across 2 lines
    When I run the multi-line scan
    Then the secret should be detected as a single finding

  Scenario: 12. Needle in a Haystack Performance
    Given a haystack of 80000 spaces with 1 embedded Stripe key
    When I run the scan
    Then it should find the key in less than 500ms

  Scenario: 13. Massive Multi-Rule Validation
    Given all secrets are loaded from the obfuscated test_data.json
    When I scan haystacks containing batches of all these secrets mixed with random text
    Then the engine must successfully process all rules without crashing
    And the majority of rules should be detected at their correct locations

  Scenario: 14. Report Formatting Options
    Given a file containing a Stripe key
    When I generate a "short" report
    Then the output should contain redacted secrets
    And the output should NOT contain full secrets
    When I generate a "full" report
    Then the output should contain full secrets
    When I generate a "nocolors" report
    Then the output should NOT contain ANSI color codes

  Scenario: 15. Streaming Input via Stdin
    Given a stream of text containing a Stripe key
    When I scan the stream
    Then it should find "stripe_api_key"
