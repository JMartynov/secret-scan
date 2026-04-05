# Task: Benchmarking & Competitive Analysis (ACTUALIZED)

## 1. Objective & Context
*   **Goal**: Evaluate the detection accuracy, recall, and false-positive rate of `secret-scan` against open secret databases and compare results with industry-standard scanning libraries.
*   **Rationale**: Establishes a data-driven baseline for the tool's performance and identifies gaps in its rule library compared to market leaders.

## 2. Research & Strategy
*   **Target Datasets**:
    *   **SecretBench**: 97,479 manually labeled secrets (15,084 true positives) from 818 GitHub repositories.
    *   **GitGuardian sample_secrets**: A repository specifically designed to test scanners (AWS, MongoDB, high-entropy strings).
    *   **FPSecretBench**: Focused on false positives reported by major tools to measure and reduce noise.
*   **Target Competitors**:
    *   **Gitleaks**: The standard for regex-based scanning (800+ rules).
    *   **TruffleHog**: Specialist in verified detectors and high-entropy secrets.
    *   **detect-secrets**: IBM-led project focused on low-noise pre-commit scanning.
*   **Comparison Metrics**:
    *   **Recall**: TP / (TP + FN) - How many secrets did we find?
    *   **Precision**: TP / (TP + FP) - How much noise did we generate?
    *   **F1-Score**: Harmonic mean of Precision and Recall.
    *   **Throughput**: Scanning speed in MB/s.

## 3. Implementation Checklist
- [ ] **Infrastructure Setup**:
    - [ ] Create `tools/benchmark_runner.py` to automate the execution of multiple scanners on a target directory.
    - [ ] Set up an isolated environment with Gitleaks, TruffleHog, and detect-secrets installed.
- [ ] **Data Acquisition**:
    - [ ] Implement a script to download/clone subsets of `SecretBench` and `sample_secrets`.
    - [ ] Integrate `FPSecretBench` to specifically test the tool's noise reduction capabilities.
- [ ] **Benchmark Execution**:
    - [ ] Run `secret-scan` and the competitor tools on each dataset.
    - [ ] Log raw findings, execution time, and memory usage to `data/benchmark_results.json`.
- [ ] **Analysis & Reporting**:
    - [ ] Create `tools/compare_results.py` to generate a comparison matrix.
    - [ ] Identify the top 10 rules missed by `secret-scan` but caught by competitors.
    - [ ] Generate `BENCHMARK_REPORT.md` with visual charts and actionable improvement tasks.

## 4. Testing & Verification (Mandatory)
- [ ] **Scoring Validation**: Run the `benchmark_runner.py` on a small, hand-crafted set of 10 secrets (5 TP, 5 FP) to ensure the scoring logic is mathematically correct.
- [ ] **Reproducibility**: Ensure the benchmark script records the exact version and flags used for each tool.

## 5. Engineering Standards
*   **Objectivity**: Use default configurations for all tools unless specific common-ground flags are required.
*   **Ethics**: Do not store or redistribute raw secrets from research datasets; results must be aggregated and anonymized.
*   **Automation**: The benchmark should be runnable with a single command to allow for regression testing after major rule updates.
