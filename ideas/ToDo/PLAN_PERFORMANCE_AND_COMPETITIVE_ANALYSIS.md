# Task: Performance Benchmarking & Competitive Analysis

## 1. Objective & Context
*   **Goal**: Establish a comprehensive performance benchmarking suite and compare the tool against industry competitors (Gitleaks, TruffleHog).
*   **Rationale**: To validate the "10-20 MB/s" target and provide empirical data for marketing and technical optimization.
*   **Files Affected**:
    *   `tests/test_performance.py` (Benchmark suite)
    *   `tools/benchmark_report.py` (Report generation)
    *   `docs/benchmarks.md` (Public data)

## 2. Research & Strategy
*   **Dataset**: Use a mix of large logs (100MB+), diverse codebases, and synthetic data with hidden secrets.
*   **Competitors**: Benchmark against `gitleaks` and `trufflehog` on the same hardware and datasets.
*   **Metrics**: Throughput (MB/s), CPU/Memory usage, Precision/Recall (F1 Score).

## 3. Implementation Checklist
- [ ] **Benchmarking Harness**: Build a script that runs the detector against standardized datasets multiple times.
- [ ] **Adversary Utility Integration**: Script the execution of competitor tools to ensure fair comparison settings.
- [ ] **Automated Reporting**: Generate Markdown/HTML reports with charts comparing speed and accuracy.
- [ ] **Profiling Integration**: Connect `cProfile` and `py-spy` to the benchmark run to identify current bottlenecks.
- [ ] **Whitepaper/Article**: Draft a technical article titled "Methods of Fast Secret Scanning: Engineering a 20MB/s Engine".

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Verify that the benchmark script correctly records timing and resource usage.
- [ ] Test the report generator with sample data.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Running the benchmark suite produces a detailed comparison table.
- [ ] **Scenario**: A performance regression is detected and fails the CI build.
- [ ] **Scenario**: The comparison report proves the tool's performance advantage in streaming modes.

## 5. Demo & Documentation
- [ ] **README.md**: Add a "Benchmarks" section with the latest results.
- [ ] **CLI**: Add a `--benchmark` flag to run a quick local performance test.

## 6. Engineering Standards
*   **Objectivity**: Benchmarks must be reproducible and use "apples-to-apples" configurations for all tools.
*   **Transparency**: Publish the datasets and methodology used for the public benchmarks.
