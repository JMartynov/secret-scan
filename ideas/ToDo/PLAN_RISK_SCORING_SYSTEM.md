# Task: Advanced Risk Scoring System

## 1. Objective & Context
*   **Goal**: Replace categorical risk levels (HIGH/MEDIUM/LOW) with a weighted heuristic score (0-100).
*   **Rationale**: Provides more granular control for security teams and reduces alert fatigue by ranking findings by "likeliness".
*   **Files Affected**:
    *   `report.py`: Update `Finding` dataclass to include `score`.
    *   `detector.py`: Update `DetectionEngine.calculate_confidence` and `SecretDetector._resolve_overlaps`.
    *   `cli.py`: Add `--min-score` flag.

## 2. Research & Strategy
*   **Formula**: `Score = (Base_Weight * Confidence) + Context_Bonus + Entropy_Adjustment - FP_Penalty`.
*   **Weights**: Tier 1 (Structured): 70; Tier 2 (Infrastructure): 40; Context: +20; High Entropy (>4.5): +15; Verified: +30; Test Marker: -50.
*   **Engine Choice**: Heuristic scoring engine implemented in Python.

## 3. Implementation Checklist
- [ ] **Finding Dataclass**: Add `score: float` to `Finding` and update `redacted_value` logic if needed.
- [ ] **Scoring Logic**: Implement the new weighted formula in `DetectionEngine.calculate_confidence`.
- [ ] **Proximity Decay**: Add a decay function so context bonuses decrease as distance from the secret increases.
- [ ] **CLI Filter**: Update `cli.py` to support `--min-score` (default 0).
- [ ] **Report Formatting**: Update `format_report` to display the numeric score alongside the risk level.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_scoring_formula`: Assert score matches expected values for various combinations of signals.
- [ ] `test_proximity_decay`: Verify context bonus drops as distance increases.
- [ ] `test_score_clamping`: Ensure scores never exceed 100 or drop below 0.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Score-Based Filtering using `--min-score 70`.
- [ ] **Scenario**: Multi-Signal Boosting (Structured + Context + Entropy > 90).
- [ ] **Scenario**: Test Data Penalty (Lowering score for "EXAMPLE_KEY").

### 4.3 Test Data Obfuscation
- [ ] Ensure `data/rules.json` has updated `base_weight` or similar metadata if required.
- [ ] Verify `test_data.json` outputs include the new scores.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Add "Risk Scoring" section showing how low-score noise is filtered.
- [ ] **`README.md`**: Document the scoring formula and the `--min-score` flag.
- [ ] **CLI Help**: Update `--threshold` help text to clarify its relationship with entropy vs. the new risk score.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, direct.
*   **Perf**: Maintain throughput by caching context analysis results during scoring.
*   **Security**: Never expose the raw secret in the scoring logs.
