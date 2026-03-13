Feature: LLM Prompt Secret Detection Resilience
  As a security auditor
  I want to ensure the detector finds needles in large haystacks
  So that obfuscation or large file sizes do not hide real leaks.

  Scenario: Needle in a Haystack (Precision & Performance)
    Given a dynamically generated haystack of 80000 characters of noise
    And a decoded stripe_api_key from test_data
    And the keyword "stripe" is injected at character position 45000
    And the secret is injected immediately following the keyword
    When I run the high-performance scan
    Then the tool must identify exactly 1 "stripe_api_key"
    And the reported line number must accurately correspond to the position

  Scenario: The Kitchen Sink Stress Test (Multi-Problem Integration)
    Given a file with multiple problems:
      | Type            | Keyword | Line |
      | github_token    | github  | 10   |
      | contextual      | password| 25   |
      | entropy_context | secret  | 40   |
    And a ReDoS attack string on line 60
    When I run the scan
    Then the engine should report 3 distinct findings
    And the ReDoS rule must be safely interrupted by timeout
    And the engine must not crash

  Scenario: Entropy Proximity Validation
    Given a text with a random GUID without keyword
    And a random high-entropy string with "access_key" keyword nearby
    When I run the scan
    Then the GUID should be flagged as "High Entropy String"
    And the string with keyword should be "Potential Secret (High Entropy + Context)"
    And the confidence for the second should be higher

  Scenario: Input Truncation
    Given an input file of 150000 characters
    And a valid aws_api_id is placed at character 10000
    And a valid slack_token is placed at character 120000
    When I run the scan with 100000 limit
    Then the "aws_api_id" must be reported
    But the "slack_token" must NOT be reported
