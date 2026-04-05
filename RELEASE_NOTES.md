# Release Notes — Production-Grade Git & GitHub Integration

**Date:** 2026-04-01  
**Version:** v3.0.0

## Summary

- **Natural Language & Contextual Detection**: Greatly improved secret detection in conversational LLM prompts. A new 100-character context window logic and robust fuzzy multi-lingual intent matching (English, Spanish, French, German) detect conversational preambles (e.g., `aquí está mi contraseña`) to dramatically boost detection confidence. Added specific rules for catching prompt leakage ("Ignore all previous instructions").
- **Performance & Scalability**: Drastically increased scanning throughput using a two-stage `re2.Set` pattern pre-filtering system, reducing overhead on large files and Git histories. Added `mmap` zero-copy memory mapping for parsing gigabyte-scale logs.
- **SIMD String Searching**: Upgraded the internal search automaton to `ahocorasick-rs` to leverage Rust-based SIMD string searching logic.
- **Advanced Risk Scoring**: Introduced a 0-100 weighted risk score based on regex weights, context proximity decay, and entropy adjustments. Dynamic risk levels (CRITICAL, HIGH, MEDIUM, LOW) replace static categorizations.
- **Core Git Integration**: Native support for scanning staged changes, working directory diffs, and historical commits.
- **Ignore & Suppression Engine**: Added support for `.secretscanignore`, `# secretscan:ignore` inline comments, and repository baselines.
- **Scalability & Performance**: Introduced **Parallelized Historical Scanning** and **Commit Caching** to handle massive repositories.
- **Actionable UX**: Surgical ANSI highlighting of secrets in the terminal and enriched remediation hints with provider documentation links.
- **CI/CD Hardening**: Added SARIF output format for GitHub Code Scanning integration and a `--fail-on-risk` flag for merge gating.

## Data & Detection

- **Generic Bearer Token Support**: Added robust detection and synthetic obfuscation for generic HTTP Authorization Bearer tokens.
- **Multi-line Detection**: Reconstructed diff blocks allow regexes to match secrets split across multiple lines (e.g., PEM keys).
- **Surgical Highlighting**: Terminal reports now highlight the exact secret within the context line using ANSI red background.
- **Remediation Engine**: Integrated official security links for AWS, GitHub, Stripe, and Google Cloud to guide developer fixes.

## Tooling

- **Risk Score Filtering**: The new `--min-score` flag allows filtering out low-confidence noise.
- **Commit Caching**: `.secretscan_cache` tracks verified SHAs to avoid redundant work in deep audits.
- **Pre-commit Hooks**: Official support via `.pre-commit-hooks.yaml` using `--mode fast`.
- **SARIF Support**: `--format sarif` enables native vulnerability visualization in GitHub's Security tab.
- **Parallel Processing**: Utilizes `ProcessPoolExecutor` for high-speed audits across multiple CPU cores.

## Testing

- `tools/benchmark.py` (Created a comprehensive benchmarking suite generating synthetic log data and high-density folders, verifying throughput in MB/s, memory metrics, and accuracy).
- `pytest tests/test_chunking.py` and `tests/test_mmap_safety.py` (Validated accurate matches exactly spanning chunk boundaries over extremely large multi-megabyte files).
- `pytest tests/test_re2_set.py` (Ensured that the linear-time RE2 sets map exactly to original regex outputs for zero false negatives).
- `pytest tests/test_acceptance.py` (Validated against 25 BDD scenarios, including Git-specific flows).
- `pytest tests/test_performance.py` (Verified 90% reduction in scan time for cached incremental audits).
- `demo.sh` (Updated to showcase performance benchmarks alongside standard detection options).

The performance updates push the bounds of parallelized analysis, making multi-gigabyte repository audits consistently robust, resource-aware, and performant.
