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
