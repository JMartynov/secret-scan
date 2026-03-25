# PLAN: Code Health & Detection Refinement

## 1. Objective & Context
*   **Goal**: Resolve overlapping findings, externalize entropy heuristics, and automate rule quality checks.
*   **Rationale**: Improve detection precision by favoring specific matches over generic ones and ensure the pattern library remains clean and safe as it scales.
*   **Files Affected**:
    *   `detector.py` (Overlap logic, Entropy factor)
    *   `obfuscator.py` (Dynamic Faker mapping)
    *   `data/**/rules.json` (Schema updates)
    *   `tools/deduplicate_rules.py` (New tool)

## 2. Research & Strategy

### 2.1 Overlap Resolution (Longest Match Wins)
*   **Problem**: A string like `AKIA1234567890EXAMPLE` might trigger an `aws-access-key` rule AND a generic `high-entropy` rule.
*   **Strategy**: Implement a "Greedy Interval Merge":
    1.  Sort all findings by `start` (ascending) and `length` (descending).
    2.  Iterate through findings; if a new finding's range is already covered by a "better" one (longer or higher confidence), discard it.
    3.  Prefer Structured Rules (Tier 1) over Entropy (Tier 4).

### 2.2 Entropy Factor Normalization
*   **Problem**: The `0.7` factor in `detector.py` is hardcoded for legacy rules.
*   **Strategy**:
    *   Add `"entropy_factor": 0.7` to specific rules in `rules.json` during migration.
    *   Update `DetectionEngine` to use `rule.get('entropy_factor', 1.0)`.

### 2.3 Dynamic Synthetic Mapping
*   **Problem**: `Obfuscator` uses a hardcoded `if/elif` chain for categories.
*   **Strategy**: 
    *   Use a registry/dictionary mapping category names (e.g., `cloud_credentials`) to `Faker` providers or custom generators.
    *   Default to `fake.password()` for unknown categories.

## 3. Implementation Checklist

### Phase 1: Engine & Obfuscator Refinement
- [ ] **Overlap Logic**: Implement `_resolve_overlaps(findings)` in `SecretDetector`.
- [ ] **Entropy Schema**: Update `detector.py` to respect `entropy_factor` from rule definitions.
- [ ] **Obfuscator Registry**: Refactor `_generate_synthetic` to use a dynamic dispatcher.

### Phase 2: Tooling & Automation
- [ ] **Deduplication Tool**: Create `tools/deduplicate_rules.py` to merge identical regex patterns across categories.
- [ ] **Rule Linter**: Update `tools/regex_lint.py` to validate the new `entropy_factor` and `category` fields.
- [ ] **CI Integration**: Draft `.github/workflows/rule-quality.yml` to run linter and deduplication checks on PRs.

## 4. Testing & Verification

### 4.1 Overlap Tests
- [ ] Create a test case in `tests/test_detector.py` where a single string triggers two rules.
- [ ] Assert that only the "winning" rule (longest/highest confidence) is returned.

### 4.2 Synthetic Data Tests
- [ ] Add a new category folder to `data/` and verify `Obfuscator` generates a fallback value without code changes.

### 4.3 Deduplication Validation
- [ ] Manually add a duplicate rule to `data/api_keys/rules.json` and verify `tools/deduplicate_rules.py` identifies and merges it.

## 5. Engineering Standards
*   **Performance**: The overlap resolution must be O(N log N) or better (sorting + single pass).
*   **Security**: Ensure ReDoS-safe regex remains a blocking requirement in the linter.
*   **Consistency**: Category names in `data/` must match the keys in the Obfuscator's dynamic mapping.
