# Task: Performance & Scalability Optimization (ACTUALIZED)

## 1. Objective & Context
*   **Goal**: Achieve 20MB/s+ scanning throughput by leveraging parallel processing and advanced regex engines.
*   **Baseline Status**: Current implementation uses Aho-Corasick for keyword filtering and `ProcessPoolExecutor` ONLY for git history. Individual file scanning and git staged/working scans are still serial.
*   **Rationale**: Large LLM logs and high-volume git repositories currently bottleneck on the single-threaded `_scan_block` loop in `detector.py`.

## 2. Research & Strategy
*   **Mechanism**: 
    *   **RE2.Set**: Implement a two-stage matching process. Use `re2.Set` to identify *all* matching rule IDs in a single pass, then run individual `finditer` calls ONLY for the confirmed hits.
    *   **Zero-Copy Scanning**: Use `mmap` for large file inputs in `cli.py` to avoid redundant string allocations.
*   **Parallelism**: Unified `ParallelScanner` class to handle all input types (files, git diffs, history) with a consistent `ProcessPoolExecutor` implementation.
*   **Chunking**: Standardize 1MB chunks with 8KB overlaps (double the current recommendation to account for longer PII/Key patterns) to ensure no secrets are missed at boundaries.

## 3. Implementation Checklist
- [ ] **RE2.Set Integration**: 
    - [ ] Refactor `DetectionEngine._initialize_rules` to populate a `re2.Set` with all `re2` rule patterns.
    - [ ] Modify `SecretDetector._scan_block` to use `re2_set.Match(text)` as a pre-filter before `finditer`.
- [ ] **Unified Parallel CLI**:
    - [ ] Refactor `cli.py` to use a worker pool for *all* scan modes (`--git-staged`, `--git-working`, and direct file paths).
    - [ ] Implement `mmap` support for the `input` file argument when size > 10MB.
- [ ] **Optimized Overlap Resolution**:
    - [ ] `detector.py`: Refactor `_resolve_overlaps` to use a more efficient interval-tree-like approach if finding count > 1000.
- [ ] **SIMD Upgrade**:
    - [ ] Update `requirements.txt` to include `ahocorasick-rs` and fallback to `pyahocorasick` if Rust bindings are unavailable.
- [ ] **Performance Tooling**:
    - [ ] Create `tools/benchmark.py` to measure throughput on various file sizes and rule densities.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `tests/test_performance.py`: Add `test_re2_set_consistency` to ensure `re2.Set` matches exactly what individual rules find.
- [ ] `tests/test_chunking.py`: Verify that secrets spanning exactly at 1MB boundaries are caught via the overlap buffer.
- [ ] `test_mmap_safety`: Ensure `mmap` handles files that are modified or truncated during scanning without crashing.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Multi-file Parallelism (Scan 100 small files in parallel and verify result order and integrity).
- [ ] **Scenario**: Large Log Throughput (Verify > 20MB/s on a 100MB synthetic log file).

### 4.3 Test Data
- [ ] Generate a 50MB `data/perf_test_large.log` using `tools/generate_test_data.py`.

## 5. Engineering Standards
*   **Safety**: RE2 is mandatory for the batch engine. Legacy regexes (with timeouts) must remain isolated to the secondary pass.
*   **Memory**: Keep peak memory usage < 2x the largest file chunk size per worker thread.
*   **Concurrency**: Ensure `DetectionEngine` instances are reused within workers to avoid the overhead of re-compiling 100+ regexes per file.
