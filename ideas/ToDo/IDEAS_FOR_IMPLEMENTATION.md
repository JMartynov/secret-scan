# Secret Scan: Implementation Roadmap & Ideas

Based on the analysis of `ideas/roadmap/`, this document outlines specific technical enhancements to evolve the `secret-scan` tool into a robust, high-performance LLM-specific security utility.

---

## 1. Multi-Tier Rule Categorization
**Source:** `recomendations1.md`
**Concept:** Move beyond a flat rule list to 4 specialized detection tiers.

### Implementation Details:
* **Refactor `data/rules.json`**: Add a `category` field to every rule:
    * `structured`: High-confidence regex (AWS, GitHub).
    * `infrastructure`: Connection strings, DB URLs, Private Keys.
    * `entropy`: High-randomness strings without fixed patterns.
    * `contextual`: Natural language prompt patterns (e.g., "my prod password is").
* **Engine Update**: Update `DetectionEngine` to process these categories with tiered logic (e.g., skip entropy checks if a structured match is already confirmed at the same location).

---

## 2. Advanced Risk Scoring System
**Source:** `recomendations1.md`
**Concept:** Replace static "HIGH/MEDIUM" labels with a weighted numeric score (0-100).

### Implementation Details:
* **Scoring Logic**:
    * Base Regex Match: +50
    * High Entropy (>4.0): +20
    * Context Keyword Match (within 50 chars): +30
    * Infrastructure Pattern: +15
* **Mapping**:
    * `CRITICAL`: >85
    * `HIGH`: 65-84
    * `MEDIUM`: 40-64
    * `LOW`: <40

---

## 3. Secret Validation Layer
**Source:** `recomendations1.md`, `recomendations2.md`
**Concept:** Verify if a detected secret is actually live and valid via external APIs.

### Implementation Details:
* **Validator Interface**: Create `validators/base.py` and specific implementations (e.g., `github.py`, `aws.py`).
* **Optional CLI Flag**: Add `--verify` to trigger these network checks for high-confidence matches.
* **Security**: Ensure validation calls are made over HTTPS and respect rate limits.

---

## 4. Parallel Scanning Architecture
**Source:** `recomendations2.md`
**Concept:** Improve performance when scanning multiple large files.

### Implementation Details:
* **CLI Update**: In `cli.py`, if multiple file paths are provided, use `concurrent.futures.ProcessPoolExecutor` to distribute scanning tasks across CPU cores.
* **Worker Logic**: Each worker processes one file and returns a list of `Finding` objects to the main process for report consolidation.

---

## 5. Git Integration (Diff Scanning)
**Source:** `recomendations2.md`
**Concept:** Facilitate use as a pre-commit or CI tool.

### Implementation Details:
* **New Flag**: Add `--staged` (or `--git`) to `cli.py`.
* **Logic**: If enabled, run `git diff --cached --unified=0` and scan only the added/modified lines. This makes scanning large repositories instantaneous.

---

## 6. Automated Rule Linting
**Source:** `speed_architecture1.md`
**Concept:** Prevent ReDoS by enforcing regex safety during development.

### Implementation Details:
* **CI Integration**: Create a GitHub Action that runs `tools/run_regexploit.py` on any PR that modifies `data/rules.json`.
* **Blocking**: Fail the build if any rule is identified as vulnerable to catastrophic backtracking.

---

## 7. Natural Language Context Patterns
**Source:** `recomendations1.md`
**Concept:** Better detection of secrets embedded in human conversation.

### Implementation Details:
* **Expand Context Rules**: Add patterns for conversational prefixes:
    * `(?i)(?:here is|this is|use|using|my|our)\s+(?:prod|production|live|real)\s+(?:api|token|key|password|secret|cred)`
* **Proximity Matching**: Increase the "context" weight if these phrases appear within 100 characters of a high-entropy string or generic token.

---

## 8. Performance: Regex Sets (Hyperscan/RE2)
**Source:** `speed_architectute.md`
**Concept:** Evaluate even faster matching for the 1600+ rule database.

### Implementation Details:
* **RE2.Set**: Investigate `re2.Set` to match multiple patterns in a single pass, further reducing the need for the Aho-Corasick + Individual Regex loop.
* **Hyperscan**: If `re2` becomes a bottleneck, implement an optional `hyperscan` backend (requires C libraries).

---

## 9. Obfuscation Mode (Privacy Masking)
**Concept**: Output the original text but with all detected secrets replaced by their redacted or hashed versions.

### Implementation Details:
* **CLI Flag**: Add `--obfuscate`.
* **Logic**: Instead of returning a report, the tool should print the entire input stream, but replace the `Finding.content` with `Finding.redacted_value`.
* **Preservation**: Ensure that non-secret parts of the text (including formatting and whitespace) are preserved exactly as in the input.

---

## 10. Extended Infrastructure & URI Patterns
**Concept**: Deepen detection for URIs, connection strings, and database-specific credentials.

### Implementation Details:
* **Pattern Expansion**: Add more robust regex for:
    * `mongodb+srv://[user:password@]host[/[database][?options]]`
    * `redis://[:password@]host[:port]`
    * `jdbc:mysql://[host:port]/[database]?user=[user]&password=[password]`
    * Generic `[scheme]://[user:password@]host` patterns for URIs.
* **Refined Validation**: Ensure that user/password groups are correctly captured even with special characters.

---

## 11. Human-Centric Language Patterns
**Concept**: Detect secrets by identifying "intent" markers in natural language.

### Implementation Details:
* **Markers**: Detect variations of "The secret code is...", "Password for the server:", "Access token for my account:", etc.
* **Multi-lingual Support**: Add markers for common languages beyond English (e.g., "Mdp:", "Contraseña:").

---

## 12. PII Layer (Personal Identifiable Information)
**Concept**: Extend the tool to detect non-secret sensitive data like emails, phone numbers, and credit cards.

### Implementation Details:
* **PII Patterns**: Add a separate rule-set or category for:
    * Credit card numbers (Luhn check validated).
    * Social Security Numbers / National IDs.
    * Physical addresses and phone numbers.
    * Personal email addresses in sensitive contexts.
* **Configurable**: Allow users to toggle PII detection separately from secret detection (e.g., `--pii`).

---

## 13. System-Wide Speed Improvements
**Concept**: Continually optimize for the 10-20 MB/s scanning target.

### Implementation Details:
* **SIMD Optimizations**: Use `ahocorasick_rs` or `hyperscan` to leverage CPU-level parallel instructions.
* **Memory Management**: Reduce allocations by using memory-mapped files or zero-copy buffers for large input streams.
* **Profiling**: Integrate a benchmark suite (`pytest-benchmark`) to track the performance impact of new rules.

---

## Summary of Comparison

| Feature | Roadmap Status | Implementation Priority |
| :--- | :--- | :--- |
| **Aho-Corasick Filter** | COMPLETED | - |
| **RE2 Integration** | COMPLETED | - |
| **Redaction/Reporting** | COMPLETED | - |
| **Risk Scoring** | MISSING | HIGH |
| **Obfuscation Mode** | MISSING | HIGH |
| **Extended Patterns (URI/DB)** | IN PROGRESS | HIGH |
| **PII Layer** | MISSING | MEDIUM |
| **Human Language Context** | IN PROGRESS | MEDIUM |
| **Git Diff Mode** | MISSING | MEDIUM |
| **Validation Layer** | MISSING | LOW |
| **Parallel Scans** | MISSING | LOW |
| **Speed Improvements** | CONTINUOUS | ONGOING |
