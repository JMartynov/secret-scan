# PLAN: Rule Quality & Security (Linting)

## 1. Objective
Ensure the pattern database is performant, secure against ReDoS, and maintains high accuracy.

## 2. Analogs & Research
- **Regexploit**: Identifies exponential backtracking in regex.
- **Safe-regex**: Node.js tool for checking ReDoS (analogous Python implementations).

## 3. Implementation Details

### 3.1 Automated Safety Checks
- Integrate `regexploit` into the development workflow.
- Every new rule must pass a "Complexity Test". If a regex has nested quantifiers like `(a+)+`, it must be rejected.
- Use `signal.alarm` watchdog (already partially implemented) as a runtime safety net.

### 3.2 Accuracy Testing
- Enhance `tools/generate_test_data.py` to generate "Near-Misses" for every new rule.
- Example: If a rule matches `ghp_[a-zA-Z0-9]{36}`, the generator should create `ghp_[a-zA-Z0-9]{35}` (too short) and `gh_p_[a-zA-Z0-9]{36}` (wrong prefix) to test the regex boundaries.

### 3.3 Rule Coverage
- Categorize rules by provider.
- Implement a script to compare `data/rules.json` against the `Secrets-Patterns-DB` to identify missing major providers.

## 4. Best Practices
- **Atomic Rules**: One regex per provider/token-type. Avoid "Mega-regex" that try to match everything.
- **Mandatory Keywords**: Every rule MUST have at least one keyword for `ahocorasick` pre-filtering.
- **DFA Preference**: Prefer patterns that are compatible with DFA engines (no backreferences) for linear-time guarantees.

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_regex_safety_checker`**: Verify that the checker correctly identifies simple ReDoS patterns (e.g., `(a+)+$`).
- **`test_mandatory_keywords`**: Assert that `DetectionEngine` fails to load if a rule is missing keywords.
- **`test_test_data_generation`**: Verify that `generate_test_data.py` produces both positive and negative samples for every rule in `rules.json`.
- **`test_near_miss_accuracy`**: Provide hand-crafted near-misses (e.g., 35-char GitHub token) and verify that the detector correctly ignores them.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Blocking Vulnerable Rule in PR**
  - Given a new rule with a nested quantifier `(.*)*`
  - When the linting tool is run
  - Then it must exit with code 1 and identify the rule as "Vulnerable to ReDoS"
- **Scenario: Rule Parity with External DBs**
  - When the coverage script is run
  - Then it must generate a report showing which major providers (AWS, GCP, Azure, GitHub) are fully covered.
- **Scenario: Runtime Watchdog Timeout**
  - Given a rule that hangs for > 1 second (simulated ReDoS)
  - When the scanner processes a matching input
  - Then the watchdog must terminate the match and log a warning without crashing the tool.
