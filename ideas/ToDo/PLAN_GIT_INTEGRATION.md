# PLAN: Git & CI Integration

## 1. Objective
Integrate the scanner into development workflows to prevent secrets from ever being committed to source control.

## 2. Analogs & Research
- **`gitleaks protect`**: Scans uncommitted changes.
- **Pre-commit framework**: A standard way to manage Git hooks.

## 3. Implementation Details

### 3.1 Diff Scanning Mode
- Implement `cli.py --git`:
    - Run `git diff --staged --unified=0` (for pre-commit).
    - Run `git diff HEAD~1 --unified=0` (for CI).
- Parse the diff to scan only the `+` (added) lines.
- **Context Awareness**: Read 3 lines of context around changes to ensure the `DetectionEngine` has enough data for contextual rules.

### 3.2 Pre-commit Hook
- Add a `.pre-commit-hooks.yaml` file to the root.
- Allow users to install via `pre-commit install`.
- Hook should fail (exit code 1) if any CRITICAL or HIGH risk secrets are found in the diff.

### 3.3 GitHub Action
- Provide a standard `.github/workflows/secret-scan.yml` template.
- Use it to scan Pull Requests.
- Support "Fail-on-Risk" configuration.

## 4. Best Practices
- **Performance**: Pre-commit hooks must be fast (<1s). Use the diff-scanning mode exclusively for hooks.
- **Allowlisting**: Support `.secretscanignore` files to allow known-safe test data in repositories.
- **History Scanning**: Add a separate command `./run.sh --history` for deep-scan of the entire Git log (use `git log -p`).

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_git_diff_parser`**: Verify that `cli.py` correctly extracts only the added lines (`+`) from raw `git diff` output.
- **`test_context_expansion`**: Ensure that scanning a diff line with context correctly identifies secrets that depend on surrounding text.
- **`test_ignore_file_parsing`**: Assert that `.secretscanignore` rules (files or regex) are correctly loaded and applied.
- **`test_exit_codes`**: Verify that `cli.py` exits with `1` if secrets are found in diff mode and `0` if clean.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Pre-commit Blockage**
  - Given I have staged a file with a Stripe key
  - When I run `pre-commit run --all-files`
  - Then the hook must fail and show the detected secret
- **Scenario: Scanning Last Commit**
  - Given a commit was just made containing a secret
  - When I run `./run.sh --git --last-commit`
  - Then the secret from the last commit must be reported
- **Scenario: Repo-Wide History Scan**
  - Given a repository with a secret committed 10 commits ago
  - When I run `./run.sh --history`
  - Then the secret must be found and reported with its original commit hash.

---

## 6. Demo Update
Update `demo.sh` to include a section for "Git Workflow Integration":
- Create a temporary git repository in the demo script.
- Stage a file with a secret and run `./run.sh --git` to show how it protects commits.

---

## 7. Documentation Update
Update `README.md`:
- Add a new section for "Git Integration".
- Document the `--git` (diff scanning) and `--history` (log scanning) flags.
- Provide instructions for installing the pre-commit hook.
