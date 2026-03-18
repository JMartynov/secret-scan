# PLAN: Advanced Risk Scoring System

## 1. Objective
Move from categorical risk levels (HIGH/MEDIUM) to a weighted heuristic score (0-100) for more nuanced security reporting.

## 2. Analogs & Research
- **GitGuardian**: Uses a proprietary scoring engine based on proximity and secret validity.
- **Bayesian Filtering**: Common in spam detection, can be adapted for "secret-likeliness".

## 3. Implementation Details

### 3.1 Scoring Formula
`Score = (Base_Regex_Weight * Confidence) + Context_Bonus + Entropy_Adjustment - False_Positive_Penalty`

| Component | Weight/Value | Description |
| :--- | :--- | :--- |
| **Tier 1 Match** | 70 | High-confidence structured pattern. |
| **Tier 2 Match** | 40 | Infrastructure/DB pattern. |
| **Context Bonus** | +20 | Keyword found within 50 characters. |
| **High Entropy** | +15 | Shannon Entropy > 4.5. |
| **Verified Valid** | +30 | If validation layer confirms the secret is live. |
| **Test Data Marker** | -50 | Pattern matches known test formats (e.g., `EXAMPLE_KEY`). |

### 3.2 Thresholds
- **90+ (CRITICAL)**: Verified valid or extremely high-confidence structured secret.
- **70-89 (HIGH)**: Clear structured match or infrastructure match with context.
- **40-69 (MEDIUM)**: High entropy string with weak context.
- **<40 (LOW)**: Possible PII or generic random string.

### 3.3 Implementation Task
- Modify `Finding` dataclass to include a `score: float` field.
- Update `detector.py` to calculate this score during the `_scan_block` phase.
- Update `report.py` to allow filtering by score (e.g., `--min-score 70`).

## 4. Best Practices
- **Proximity Weighting**: Use a decay function for context. A keyword right next to the secret is worth more than one 10 lines away.
- **Multi-Factor Verification**: If a string matches a regex AND has high entropy AND has context, the score should exceed 100 but be capped.

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_scoring_weights`**: Verify that `Finding.score` accurately reflects the formula with mocked inputs.
- **`test_context_decay`**: Assert that context bonus decreases as distance between secret and keyword increases.
- **`test_score_capping`**: Ensure that no `Finding.score` exceeds 100, even with multiple bonuses.
- **`test_negative_scoring`**: Verify that "Test Data Markers" correctly penalize/lower the score.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Score-Based Filtering**
  - Given the detector has found 5 findings with scores [20, 50, 65, 80, 95]
  - When I run the report with `--min-score 70`
  - Then only 2 findings should be visible in the output
- **Scenario: Proximity Bonus Impact**
  - Given a text "password is: abc123random" (High Proximity)
  - And a text "The system has a password. Somewhere below it uses: abc123random" (Low Proximity)
  - When I scan both
  - Then the score for the first should be significantly higher than the second
- **Scenario: Multi-Signal Boosting**
  - When I scan "My AWS key: AKIA..." (Structured + Context + High Entropy)
  - Then the finding should have a score > 90
