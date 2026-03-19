# PLAN: Multi-Tier Rule Categorization & PII Layer

## 1. Objective
Evolve the flat rule structure into a multi-tier system that supports different detection strategies and extends coverage to Personal Identifiable Information (PII).

## 2. Analogs & Research
- **Microsoft Presidio**: Uses "Recognizers" categorized by entity type.
- **Google Cloud DLP**: Categorizes by "InfoTypes" (Global vs. Regional).
- **GitGuardian**: Separates "Secrets" from "Sensitive Information".

## 3. Implementation Details

### 3.1 Tiered Structure
Refactor `data/rules.json` to include a `tier` field:
- **Tier 1 (Structured)**: High-confidence, fixed-format tokens (AWS, Stripe). Match = Immediate High Risk.
- **Tier 2 (Infrastructure)**: Semi-structured credentials (DB URLs, SSH Keys). Requires keyword confirmation.
- **Tier 3 (Contextual)**: Soft patterns (Passwords in comments, prompts). Heavy reliance on surrounding text.
- **Tier 4 (Entropy)**: Fallback for random strings. Lowest confidence without context.

### 3.2 PII Layer
Add a new rule file `data/pii_rules.json`:
- **Financial**: Credit Cards (Regex + Luhn Check), Bank Account numbers.
- **Identity**: SSNs, Passport numbers, Driver's Licenses (Regional patterns).
- **Contact**: Emails, Phone numbers, Physical addresses.
- **Healthcare**: HIPAA-related identifiers.

### 3.3 Engine Integration
- Implement `SecretDetector(include_pii=True)`.
- Use `ahocorasick` to load both secret and PII keywords into a single automaton pass.
- **Optimization**: Structured rules (Tier 1) should "shadow" lower tiers. If an AWS key is found, don't run a generic entropy check on the same string.

## 4. Best Practices
- **Luhn Algorithm**: Mandatory for Credit Card validation to reduce false positives.
- **Regional Scoping**: Allow users to specify country codes to limit PII scanning (e.g., `--pii-region US,UK`).
- **Checksums**: Many ID formats (like SSNs) have internal checksums; implement these in Python `validators/` to filter regex noise.

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_rule_tier_loading`**: Verify `DetectionEngine` correctly parses and assigns tiers from `rules.json`.
- **`test_luhn_validator`**: Test `validators.luhn_check` with valid/invalid credit card numbers (VISA, Mastercard).
- **`test_pii_regex_boundaries`**: Test email/phone regex with edge cases (e.g., `user+tag@domain.co.uk`, `+1-555-0100`).
- **`test_tier_shadowing`**: Provide a string that matches both a Tier 1 rule (AWS) and Tier 4 (Entropy). Assert only Tier 1 is reported.

### 5.2 Acceptance Tests (BDD)
- **Scenario: PII Detection Toggle**
  - Given the detector is initialized with `--pii`
  - When I scan "My email is test@example.com"
  - Then it should find "email_address"
- **Scenario: Regional PII Filtering**
  - Given PII scanning is enabled for region "UK"
  - When I scan a US-formatted phone number "(555) 123-4567"
  - Then it should NOT report any findings
- **Scenario: Financial Data Validation**
  - When I scan a 16-digit random number that FAILS Luhn check
  - Then it should NOT report a "credit_card" finding

---

## 6. Demo Update
Update `demo.sh` to include a section for "PII Detection":
- Add sample emails, phone numbers, and (valid/invalid) credit card numbers.
- Show how the tool distinguishes between these categories using the new tiered reporting.

---

## 7. Documentation Update
Update `README.md`:
- Add a new section for "PII Detection".
- Document the `--pii` flag and list the types of PII detected (emails, phones, credit cards).
- Explain the new multi-tier categorization of findings.
