# Task: Extend GitHub Scan to Include Commit History

Use this template when planning and implementing new features or rules for the `secret-scan` tool.

## 1. Objective & Context
*   **Goal**: Extend the GitHub repository scanning functionality to check not only each branch, but also every individual commit within those branches.
*   **Rationale**: Currently, scanning might only check the latest state of branches or specific files. Secrets can be introduced and subsequently removed in intermediate commits. Scanning the entire commit history ensures that no historical secrets are leaked.
*   **Files Affected**:
    *   `src/git_engine.py` (Git operations and history traversal)
    *   `src/cli.py` (New CLI arguments for commit scanning and limits)
    *   `scan_repos.py` (Orchestration of repository scans)
    *   `tests/test_git_engine.py` (New tests for commit traversal)
    *   `README.md` (Documentation for new options)

## 2. Research & Strategy
*   **Pattern Analysis**: The focus is on robust `git` operations. We need to effectively use `git log` or `git rev-list` to traverse the commit tree for each branch without redundantly scanning shared history (e.g., handling merge commits efficiently).
*   **Engine Choice**: Enhance the `git_engine.py` or `scan_repos.py` logic. We must use memory-efficient and fast git commands to iterate through file diffs or historical file states per commit.
*   **Risk Tier**: Infrastructure / Core CLI feature.

## 3. Implementation Checklist
- [ ] **Surgical Edits**: 
    - Update `git_engine.py` to support a `scan_history` mode.
    - Implement logic to stream file contents from historical commits (e.g., using `git show <commit>:<file>` or parsing `git log -p`) to the `detector`.
- [ ] **New CLI Options**: Add arguments to control history scanning:
    - `--scan-history`: Flag to enable checking every commit.
- [ ] **Metric Limits**: Implement limits for the scan (by default, no limits):
    - `--limit-commits`: Maximum number of commits to scan per branch (default: 0 / no limit).
    - `--limit-depth`: Maximum history depth in days (e.g., scan only the last 30 days).
- [ ] **Performance**: Ensure that checking historical commits does not drastically reduce performance. Optimize by avoiding full working tree checkouts and instead piping file blobs directly to the scanner.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Add unit tests in `tests/test_git_engine.py` to verify that all commits in a mock repository's history are traversed when the flag is enabled.
- [ ] Verify that the limit options correctly halt traversal.

### 4.2 Acceptance Testing (BDD)
- [ ] Add a new `Scenario` to `tests/acceptance.feature` describing a secret added in commit A and removed in commit B.
- [ ] Verify that the scanner finds the secret when history scanning is enabled, but not when disabled.

### 4.3 Test Data Obfuscation
- [ ] Ensure any mock git repositories created for testing use fake, obfuscated secrets to prevent triggering real security alerts.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Add a demonstration of scanning a repository's history and finding a "deleted" secret.
- [ ] **`README.md`**: Document the `--scan-history` and `--limit-*` flags under the usage instructions.
- [ ] **CLI Help**: Verify the new flags appear correctly in `secret-scan --help` with appropriate default descriptions (e.g., "by default no limit").

## 6. Engineering Standards
*   **Perf**: History scanning is I/O intensive. Use efficient git subprocess calls and parallelize blob scanning where applicable.
*   **Security**: Ensure secrets found in history are still properly obfuscated in final reports.