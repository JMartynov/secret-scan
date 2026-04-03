# Performance Benchmark Results

| Scenario | Files Scanned | Total Time (s) | Init Time (s) | Scan Time (s) | Throughput (MB/s) | Files/sec | Secrets Found | Peak Mem (MB) |
|----------|---------------|----------------|---------------|---------------|-------------------|-----------|---------------|---------------|
| Large Single File (50MB) | 1 | 16.18 | 2.11 | 14.07 | 3.55 | 0.07 | 0 | 99.39 |
| Directory of 100 Small Files (~48MB Total) | 100 | 40.03 | 2.11 | 37.92 | 1.28 | 2.64 | 1 | 0 |
| Git History (50 Commits) Pytest | 50 | 18.04 | 2.11 | 15.93 | 0.0 | 3.14 | 5 | 0 |

## Metric Definitions
- **Files Scanned**: The number of items (files or commits) processed.
- **Total Time**: End-to-end execution time including CLI startup and rule loading.
- **Init Time**: Time taken to load regex rules and compile the Aho-Corasick automaton & RE2 sets.
- **Scan Time**: Estimated time spent purely scanning (Total Time minus Init Time).
- **Throughput**: Megabytes scanned per second (based on Scan Time).
- **Files/sec**: Processing rate per item.
- **Peak Mem**: Peak memory consumption increase observed during the child process execution.
