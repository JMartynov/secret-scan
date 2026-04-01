# Task: Performance & Scalability Optimization

## 1. Objective & Context
*   **Goal**: Achieve 20MB/s+ scanning throughput by leveraging parallel processing and advanced regex engines.
*   **Rationale**: To handle large-scale LLM logs and real-time streams without becoming a bottleneck in the pipeline.
*   **Files Affected**:
    *   `detector.py`: Implement `RE2.Set` support in `DetectionEngine`.
    *   `cli.py`: Optimize `ProcessPoolExecutor` usage and chunking logic.
    *   `tools/benchmark_report.py`: New tool for tracking performance gains.

## 2. Research & Strategy
*   **Mechanism**: Use `re2.Set` for one-pass matching of multiple structured patterns.
*   **Parallelism**: Process multi-file batches using `ProcessPoolExecutor` with optimized chunk sizes (1MB chunks / 4KB overlaps).
*   **Memory**: Utilize `mmap` for reading large files to reduce buffer allocation overhead.
*   **Engine Choice**: `re2.Set` (C++) for structured rules; SIMD-optimized Aho-Corasick.

## 3. Implementation Checklist
- [ ] **RE2.Set Integration**: Refactor `DetectionEngine._initialize_rules` to group structured patterns into a `re2.Set`.
- [ ] **Zero-Copy Scanning**: Modify `SecretDetector._scan_block` to work with memory-mapped buffers.
- [ ] **Parallel Chunking**: Implement a more robust chunking strategy in `cli.py` that maintains line-number integrity across worker processes.
- [ ] **SIMD Optimization**: Ensure `ahocorasick_rs` is used if available for even faster keyword filtering.
- [ ] **Bottleneck Analysis**: Use `cProfile` and `line_profiler` to identify and eliminate hotspots in `_resolve_overlaps`.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_chunk_boundary_overlap`: Verify secrets split across 1MB chunks are correctly detected.
- [ ] `test_re2_set_parity`: Assert `re2.Set` matches exactly what individual `re2` patterns match.
- [ ] `test_parallel_merge_integrity`: Ensure findings from different workers are merged correctly without duplicates.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Bulk Scan Performance (100MB of logs scanned in < 5 seconds).
- [ ] **Scenario**: Large File Streaming (Accurate line numbers for secrets at the end of a 1GB file).
- [ ] **Scenario**: Consistency Check (Parallel vs. Serial results must be identical).

### 4.3 Test Data Obfuscation
- [ ] Use a standardized 10MB "Performance Test Set" in `tests/data/perf_data.json`.

## 5. Demo & Documentation
- [ ] **`demo.sh`**: Include a performance benchmark section that prints MB/s throughput.
- [ ] **`README.md`**: Update "Performance" section with new benchmarks on standard hardware.
- [ ] **`docs/ARCHITECTURE.md`**: Document the parallel scanning and `re2.Set` implementation.

## 6. Engineering Standards
*   **Tone**: Senior Engineer, data-driven.
*   **Perf**: Target: 20MB/s+ on a 4-core machine.
*   **Security**: Ensure parallel processing doesn't leak sensitive data into IPC channels; keep content redacted until the final report.
