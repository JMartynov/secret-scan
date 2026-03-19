# PLAN: Performance & Scalability Optimization

## 1. Objective
Achieve 20MB/s+ scanning throughput on modern hardware while supporting large-scale streaming and multi-file batches.

## 2. Analogs & Research
- **Ripgrep (rg)**: Uses the Rust `regex` crate and memory-mapped files.
- **Hyperscan**: Intel's library for high-speed multi-pattern matching.

## 3. Implementation Details

### 3.1 Parallel Scanning
- Use `concurrent.futures.ProcessPoolExecutor` in `cli.py`.
- For directories: Assign one file per worker.
- For single massive files: Split into chunks and assign to workers (ensuring overlap buffers are maintained).

### 3.2 Advanced Engines
- **RE2.Set**: Implement a transition from `ahocorasick` -> `re2.finditer` to a single `re2.Set` pass for structured rules. `re2.Set` matches multiple patterns in one NFA/DFA pass.
- **Hyperscan Backend (Optional)**: If rule count exceeds 2000, provide an optional backend using `python-hyperscan`. This requires `libhyperscan` but offers Gbit/s performance.

### 3.3 Memory Optimization
- Use `mmap` for file reading to avoid large buffer allocations.
- Implement "Zero-Copy" reporting where findings store offsets rather than string copies until the final report generation.

## 4. Best Practices
- **SIMD**: Ensure `pyahocorasick` or `ahocorasick_rs` is compiled with SIMD support (SSE4.2/AVX2).
- **Chunking**: Use 1MB chunks with 4KB overlaps for streaming to balance memory use and detection accuracy.
- **Profiling**: Use `cProfile` and `line_profiler` to identify bottlenecks in the `DetectionEngine`.

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_chunking_boundary_integrity`**: Verify that a secret split exactly at a 1MB boundary is detected correctly using the overlap buffer.
- **`test_parallel_result_merging`**: Assert that `cli.py` correctly consolidates and deduplicates findings from multiple worker processes.
- **`test_re2_set_functional_parity`**: Ensure `RE2.Set` matches exactly the same strings as individual `RE2` regex calls.
- **`test_mmap_handling`**: Assert that `detector.py` can read from memory-mapped files without errors.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Bulk Scan Performance**
  - Given a directory of 100 files (10MB total) with 10 hidden secrets
  - When I run a bulk scan
  - Then the scan should complete in less than 2 seconds
- **Scenario: Large File Streaming**
  - Given a single 100MB file with a secret at the 50MB and 99.9MB positions
  - When I scan the file via pipe
  - Then both secrets should be reported with accurate line numbers
- **Scenario: Parallel vs. Serial Consistency**
  - When I scan the same directory in serial mode and parallel mode
  - Then both reports must have identical findings

---

## 6. Demo Update
Update `demo.sh` to include a section for "High-Performance Scanning":
- Increase the size of the performance benchmark file.
- Add a summary of the scanning speed (MB/s) to the demo output to showcase optimization gains.

---

## 7. Documentation Update
Update `README.md`:
- Update the "Performance" section with new benchmarks.
- Briefly mention the high-performance backends (RE2/Hyperscan) and parallel scanning support.
