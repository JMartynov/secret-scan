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
