# Task: Multi-Tier Rule Categorization & PII Layer

## 1. Objective & Context
*   **Goal**: Implement a 4-tier rule taxonomy and add a dedicated layer for Personal Identifiable Information (PII).
*   **Rationale**: Better organization of rules improves engine optimization (shadowing) and expands the tool's utility to privacy compliance.
*   **Files Affected**:
    *   `detector.py`: Update `DetectionEngine` to handle tiered logic and PII loading.
    *   `data/`: Refactor directory structure to match tiers.
    *   `data/pii/`: New directory for PII rules.
    *   `cli.py`: Add `--pii` and `--pii-region` flags.

## 2. Research & Strategy
*   **Tiers**: 1: Structured (AWS); 2: Infrastructure (DB URL); 3: Contextual; 4: Entropy.
*   **PII Rules**: Emails, SSNs, Credit Cards (Regex + Luhn), Phone numbers.
*   **Engine Choice**: Aho-Corasick for combined keyword search across both Secrets and PII.

## 3. Implementation Checklist
- [ ] **Taxonomy Refactor**: Move rules into `data/{tier_name}/rules.json` and update `_load_all_rules`.
- [ ] **PII Implementation**: Add `data/pii/rules.json` with basic patterns.
- [ ] **Luhn Validator**: Implement `validators/luhn.py` for credit card verification.
- [ ] **Tier Shadowing**: Modify `SecretDetector._resolve_overlaps` to ensure Tier 1 matches suppress Tier 4 (entropy) hits on the same text.
- [ ] **Regional Scoping**: Add logic to filter PII rules by region (e.g., US SSN vs. UK National Insurance).

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_tier_loading`: Verify rules are correctly categorized during initialization.
- [ ] `test_luhn_check`: Test with valid and invalid credit card numbers.
- [ ] `test_tier_shadowing`: Assert that an AWS key isn't also reported as "High Entropy String".

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: PII Detection (e.g., scanning for emails/phones with `--pii`).
- [ ] **Scenario**: Financial Data Validation (Luhn check).
- [ ] **Scenario**: Regional Filtering (US-only SSN scan).

### 4.3 Test Data Obfuscation
- [ ] Run `python3 tools/generate_test_data.py`.
- [ ] **Security**: Ensure PII samples in `test_data.json` are synthetic and pass GitHub checks.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Add "PII and Tiered Detection" section.
- [ ] **`README.md`**: List supported PII types and explain the tier system.
- [ ] **CLI Help**: Document the new `--pii` and `--pii-region` flags.

## 6. Engineering Standards
*   **Tone**: Senior Engineer.
*   **Perf**: Ensure PII rules don't increase the keyword automaton size excessively.
*   **Security**: PII is highly sensitive; ensure redaction is strictly applied.
