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
