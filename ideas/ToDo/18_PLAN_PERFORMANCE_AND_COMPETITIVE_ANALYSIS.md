# Task: Performance Benchmarking & Competitive Analysis

## 1. Objective & Context
*   **Goal**: Establish a continuous benchmarking suite to compare the engine's speed and accuracy against industry competitors.
*   **Rationale**: To validate our performance claims (10-20 MB/s) and ensure we maintain a technical advantage over tools like Gitleaks and TruffleHog.
*   **Files Affected**:
    *   `tests/test_performance.py`: Benchmark runner.
    *   `tools/benchmark_report.py`: Report and chart generator.
    *   `docs/BENCHMARKS.md`: Public-facing results.

## 2. Research & Strategy
*   **Competitors**: Gitleaks, TruffleHog, Ripgrep (as speed baseline).
*   **Datasets**: 1GB of mixed logs, 500MB of diverse source code, and 100MB of synthetic data with hidden secrets.
*   **Metrics**: Throughput (MB/s), Memory usage (RSS), Precision/Recall, and False Positive rate.

## 3. Implementation Checklist
- [ ] **Benchmark Runner**: Implement a standardized script that executes all tools under identical conditions.
- [ ] **Adversary Utility Harness**: Create wrappers for competitor tools to run them with "Balanced" settings.
- [ ] **Automated Charting**: Use `matplotlib` or `plotly` to generate visual comparisons of throughput and memory efficiency.
- [ ] **Regression Detection**: Integrate benchmarks into the CI/CD pipeline to flag any commit that drops performance by > 5%.
- [ ] **Technical Article**: Draft a whitepaper on "The Engineering of High-Speed Secret Detection: RE2 vs. Standard Engines".

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_benchmark_accuracy`: Verify that the runner correctly records timing and resource metrics.
- [ ] `test_competitor_execution`: Assert that competitor tools are being called with the intended configuration.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Performance Report (System generates a detailed PDF report comparing the latest build to competitors).
- [ ] **Scenario**: Speed Regression (CI build fails after a complex rule addition drops throughput below the 10 MB/s floor).

### 4.3 Test Data Obfuscation
- [ ] All datasets used for public benchmarks must be entirely synthetic.

## 5. Demo & Documentation
- [ ] **`README.md`**: Add a badge showing current throughput (e.g., "Scanning Speed: 18.4 MB/s").
- [ ] **`docs/BENCHMARKS.md`**: Publish regularly updated comparison tables.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, data-driven.
*   **Ethics**: Benchmarks must be fair, transparent, and reproducible by third parties.
*   **Perf**: The benchmark runner itself must have minimal overhead on the system being tested.
