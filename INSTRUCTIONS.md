# Instructions for Adding New Rules to the Secret Scanner

This document outlines the process for adding new secret detection rules to the project, leveraging the existing utility scripts.

## Adding New Rules

To ensure consistency, quality, and maintainability, follow these steps when adding new secret detection rules:

### Step 1: Define the Rule in Source Repository

1.  **Create Rule Files:** Add your new rule definitions in YAML format (`patterns.yml`) within the `secret-scanning-custom-patterns` repository. Organize them into appropriate subdirectories (e.g., `api_keys`, `database_credentials`, `tokens`).
2.  **Rule Schema:** Each rule should adhere to the schema observed in existing files, including:
    *   `id`: A unique identifier for the rule.
    *   `name`: A human-readable name.
    *   `category`: The external category (e.g., 'aws', 'mongo').
    *   `regex` or `pattern`: The core regular expression for detection. Include `start`, `end`, `additional_match`, and `additional_not_match` if necessary.
    *   `test_data`: Example positive and negative strings for testing. Ensure valid secrets are provided and `DUMMY_IGNORE` is used appropriately for negative test cases.

### Step 2: Parse and Normalize Rules

1.  **Extract Rules:** Run `python tools/parse_rules.py`. This script will parse all `patterns.yml` files from the cloned repositories and consolidate them into `tools/parsed_rules.json`.
2.  **Migrate and Normalize:** Execute `python tools/migrate_rules.py`. This script performs the following critical tasks:
    *   **Categorization:** Maps external categories to internal project categories (e.g., 'database' -> `database_credentials`).
    *   **Regex Normalization:** Cleans and standardizes regex patterns, ensuring compatibility with the RE2 engine (e.g., converting `\Z` to `\z`). It also wraps the core pattern in a capturing group for better secret extraction and applies non-capturing groups for start/end anchors.
    *   **Entropy Management:** Applies entropy requirements based on category and rule ID, whitelisting specific low-entropy secrets (e.g., `tru_api_secret`, `sendbird_api_key`) to prevent false negatives.
    *   **Deduplication:** Identifies and merges duplicate rules, ensuring a single, authoritative version of each rule exists.
    *   **Output:** Overwrites existing `data/<category>/rules.json` files with the migrated and normalized rules.

### Step 3: Generate and Update Test Data

1.  **Generate/Clean Test Data:** Run `python tools/migrate_tests.py`. This script:
    *   Loads the migrated rules from `tools/parsed_rules.json`.
    *   Cleans and regenerates test data in `data/<category>/test_data.json`, ensuring `DUMMY_IGNORE` artifacts are removed from positive samples and that test data reflects rule requirements. It overwrites existing test data for each rule ID to ensure freshness.
2.  **Manual Test Data Adjustment (If Necessary):** For complex rules or specific edge cases not covered by automated generation, manually edit the relevant `data/<category>/test_data.json` file to add or refine positive and negative examples.

### Step 4: Verify Rule Quality and Safety

1.  **Static Regex Analysis:** Run `python tools/regex_lint.py` and `python tools/run_safe_regex.py` to check for common regex pitfalls like nested repetitions, greedy wildcards, and exponential backtracking. Address any warnings or critical issues identified.
2.  **ReDoS Vulnerability Check:** Execute `python tools/run_redoctor.py` to scan for potential Regular Expression Denial of Service (ReDoS) vulnerabilities. Address any identified issues by refining the regex patterns.
3.  **Performance Test:** Run `python tools/stress_test.py` with a large input file (e.g., 10MB of random data with injected secrets) to ensure no performance regressions are introduced by new rules.

### Step 5: Integrate and Finalize

1.  **Update Obfuscator (If Necessary):** If new secret types require specific synthetic generation logic (e.g., Stripe, SendGrid, Twilio), update the `_generate_synthetic` method in `obfuscator.py`.
2.  **Run Full Test Suite:** Execute `pytest` to run all tests, including unit, integration, and acceptance tests (`tests/test_*.py`, `tests/test_acceptance.py`). Address any remaining failures.
3.  **Update Documentation:**
    *   Modify `README.md` to include new supported secret categories and the updated rule count.
    *   Update `INSTRUCTIONS.md` (this file) with any new workflows or conventions learned during the process.
4.  **Commit Changes:**
    *   Use `git status` to review all changes.
    *   Use `git add .` to stage all changes.
    *   Create a concise and informative commit message summarizing the additions (e.g., "feat: Add new rule categories and update detection logic").
    *   Commit the changes: `git commit -m "Your descriptive commit message"`.
    *   Push to the remote repository: `git push origin <your-branch-name>`.
5.  **Cleanup:** Remove temporary tools and cloned repositories:
    ```bash
    rm -f tools/parse_rules.py tools/parsed_rules.json tools/migrate_rules.py tools/migrate_tests.py tools/stress_test.py tools/deduplicate_rules.py tools/clean_dummy.py
    rm -rf secret-scanning-tools secret-scanning-custom-patterns
    ```

By following these steps, new rules can be safely and effectively integrated into the project, ensuring high detection quality, safety, and performance.
