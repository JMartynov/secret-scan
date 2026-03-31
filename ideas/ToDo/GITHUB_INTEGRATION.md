# PLAN: Production-Grade Git & GitHub Integration

This plan outlines the integration of the Secrets Leak Detector into the Git lifecycle and GitHub ecosystem. It addresses critical gaps identified in initial designs, focusing on performance, accuracy, and developer experience.

---

## ✅ Design Strengths
- **Pre-commit Prevention**: Blocks secrets before they reach the repository history.
- **CI Enforcement**: Automated policy checks on every Pull Request.
- **Diff-Based Efficiency**: Scans only staged changes to keep hooks fast and scalable.
- **Context-Aware**: Uses ±3 lines of context to enable sophisticated detection rules.

---

## ⚠️ Identified Risks & Mitigation Strategies

### 1. Diff Parsing Edge Cases (Split/Multi-line Secrets)
**Risk**: Secrets split across lines or multi-line blocks (PEM keys) are missed by line-by-line scanning.
**Fix**: Group consecutive `+` lines into logical blocks/chunks before scanning. Reconstruct these blocks to allow regexes to match across line breaks.

### 2. File Lifecycle (Renames & Moves)
**Risk**: Standard diffs might miss content in renamed or moved files.
**Fix**: Use `git diff --staged --name-status` to track Added (A), Modified (M), and Renamed (R) files. Handle binary-to-text transitions explicitly.

### 3. Performance in Hooks (<1s Target)
**Risk**: 1750+ rules + entropy checks can exceed the 1-second budget for pre-commit hooks.
**Fix**: Implement `--mode fast` for hooks. This mode will:
- Skip or reduce entropy scope.
- Use only high-confidence regex rules.
- Limit input size per file and per diff block aggressively.

### 4. False Positive Management
**Risk**: `.secretscanignore` is insufficient for fine-grained control.
**Fix**:
- **Inline Ignores**: Support `# secretscan:ignore` or `// secretscan:ignore`.
- **Rule Suppression**: Support `ignore-rule: aws-access-key` metadata in comments.
- **Baselines**: Use `secretscan --baseline baseline.json` to ignore existing legacy secrets.

### 5. Developer UX & Friction
**Risk**: Opaque failures lead to developers bypassing hooks.
**Fix**:
- Show ANSI-colorized, diff-highlighted output of the offending line.
- Provide clear remediation hints: "Move this to an environment variable" or "Rotate key immediately".

### 6. CI Scope & Fragility
**Risk**: `HEAD~1` is fragile in PRs with multiple commits or rebases.
**Fix**: Use `git diff origin/main...HEAD` (or the target branch) to scan the entire PR change set.

---

## 🚀 Recommended Operation Modes

| Mode | Target | Characteristics |
| :--- | :--- | :--- |
| `fast` | Pre-commit | High-confidence regex, no/low entropy, strict timeouts, sub-second latency. |
| `balanced` | Local Dev | Full rule set, standard entropy, context-aware. |
| `deep` | CI / History | Full rule set, deep entropy, multi-line reconstruction, no time limits. |

---

## 🧠 Integrated Task List

### Phase 1: Git Diff Engine (Core)
- [ ] Implement `--git-staged`, `--git-working`, and `--git-branch` flags.
- [ ] Parse `git diff --staged --unified=3` (staged) and `git diff --text` (skip binaries).
- [ ] **Mandatory**: Group contiguous `+` lines into blocks before scanning.
- [ ] Implement a "Reconstructor" for multi-line secrets (e.g., Private Keys).
- [ ] Handle file status (A, M, R) via `--name-status`.

### Phase 2: Performance Modes
- [ ] Implement `--mode {fast, balanced, deep}`.
- [ ] Optimize rule execution: Aho-Corasick pre-filtering is mandatory in `fast` mode.
- [ ] Add input size limits and file size caps (e.g., skip files > 1MB in hooks).

### Phase 3: Ignore & Suppression Layer
- [ ] Support `.secretscanignore`.
- [ ] Implement inline ignore comments (`secretscan:ignore`).
- [ ] Implement rule-level suppression.
- [ ] Implement **Baseline Support**: `--baseline <file>` to ignore existing noise.

### Phase 4: Pre-commit Integration
- [ ] Create `.pre-commit-hooks.yaml`.
- [ ] Default to `fast` mode.
- [ ] Ensure clear failure output with exact line numbers and risk levels.

### Phase 5: CI Integration (GitHub Actions)
- [ ] Create a reusable GitHub Action template.
- [ ] Use `base...HEAD` diff logic for PRs.
- [ ] Implement `--format sarif` for GitHub Code Scanning UI integration.
- [ ] Add `--fail-on-risk` flag to gate merges.

### Phase 6: History Scanning (Scalability)
- [ ] Implement `--history` using `git log -p`.
- [ ] Add `--since` and `--max-commits` flags.
- [ ] Parallelize scanning for large repositories.
- [ ] Implement **Commit Caching**: Do not re-scan already verified commit SHAs.

### Phase 7: Developer UX
- [ ] ANSI highlighting for offending secrets in the terminal.
- [ ] "Fix suggestion" engine for different secret types (e.g., AWS vs GitHub).
- [ ] Add verbosity levels for troubleshooting.

### Phase 8: Testing Expansion
- [ ] Multi-line secret detection tests.
- [ ] Diff edge case tests (renames, binary transitions).
- [ ] Performance benchmarks on "dirty" repositories.
- [ ] Large repo simulation (>10k commits).

### Phase 9: Advanced Features
- [ ] Secret rotation hints (link to provider docs).
- [ ] IDE integration hooks (LSP-compatible diagnostic output).

---

## 🛡️ Mandatory Workflow Integration
Every task must adhere to the global obligatory steps:
1. **Linting**: Run `regex_lint.py` on any rule additions.
2. **Agentic Review**: Perform `git diff main` review of all architectural changes.
3. **Tests**: All 18 BDD scenarios + new Git-specific tests must pass.
4. **Documentation**: Update `README.md`, `RELEASE_NOTES.md`, and `INSTRUCTIONS.md`.
5. **Demo**: Update `demo.sh` with a Git workflow section (staged scan demo).
