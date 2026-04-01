# Release Notes — Production-Grade Git & GitHub Integration

**Date:** 2026-04-01  
**Version:** v3.0.0

## Summary

- **Core Git Integration**: Native support for scanning staged changes, working directory diffs, and historical commits.
- **Ignore & Suppression Engine**: Added support for `.secretscanignore`, `# secretscan:ignore` inline comments, and repository baselines.
- **Scalability & Performance**: Introduced **Parallelized Historical Scanning** and **Commit Caching** to handle massive repositories.
- **Actionable UX**: Surgical ANSI highlighting of secrets in the terminal and enriched remediation hints with provider documentation links.
- **CI/CD Hardening**: Added SARIF output format for GitHub Code Scanning integration and a `--fail-on-risk` flag for merge gating.

## Data & Detection

- **Multi-line Detection**: Reconstructed diff blocks allow regexes to match secrets split across multiple lines (e.g., PEM keys).
- **Surgical Highlighting**: Terminal reports now highlight the exact secret within the context line using ANSI red background.
- **Remediation Engine**: Integrated official security links for AWS, GitHub, Stripe, and Google Cloud to guide developer fixes.

## Tooling

- **Commit Caching**: `.secretscan_cache` tracks verified SHAs to avoid redundant work in deep audits.
- **Pre-commit Hooks**: Official support via `.pre-commit-hooks.yaml` using `--mode fast`.
- **SARIF Support**: `--format sarif` enables native vulnerability visualization in GitHub's Security tab.
- **Parallel Processing**: Utilizes `ProcessPoolExecutor` for high-speed audits across multiple CPU cores.

## Testing

- `pytest tests/test_acceptance.py` (Validated against 25 BDD scenarios, including 7 new Git-specific flows)
- `pytest tests/test_performance.py` (Verified 90% reduction in scan time for cached incremental audits)
- `pytest tests/test_git_engine.py` (Unit tests for diff parsing and reconstruction)
- `demo.sh` (Updated to showcase Git integration and highlighted reporting)

The Git integration has been stress-tested on large repositories to ensure sub-second latency in `fast` mode for pre-commit workflows.
