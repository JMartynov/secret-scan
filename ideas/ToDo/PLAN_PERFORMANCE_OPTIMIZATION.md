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
