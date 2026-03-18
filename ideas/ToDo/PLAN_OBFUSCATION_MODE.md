# PLAN: Obfuscation & Privacy Masking

## 1. Objective
Allow users to redact sensitive data from logs or prompts while preserving the rest of the text for debugging or LLM processing.

## 2. Analogs & Research
- **Microsoft Presidio (Anonymizer)**: Provides masking, hashing, and synthetic data replacement.
- **DLP (Data Loss Prevention)**: Corporate tools for real-time redaction.

## 3. Implementation Details

### 3.1 Obfuscation Engine
- Implement `cli.py --obfuscate`.
- The engine must perform "In-Place" replacement.
- **Mapping**:
    - Default: `sk_l...j012` (First 4, Last 4).
    - Hashed: `sha256(secret)` (Useful for debugging without exposure).
    - Synthetic: Replace with a fake key of the same format (e.g., `sk_live_REPLACED`).

### 3.2 Stream Preservation
- Use a "Sliding Window" to detect and replace secrets in real-time as data flows through a pipe.
- Ensure that non-matched text is written to `stdout` immediately to avoid perceived latency in interactive pipes.

### 3.3 CLI Integration
```bash
cat logs.txt | ./run.sh --obfuscate > clean_logs.txt
```

## 4. Best Practices
- **Consistent Masking**: If the same secret appears twice, it should be masked the same way (especially if using hashing) to maintain debugging utility.
- **Zero-False-Redaction**: In obfuscation mode, prioritize precision. Redacting a normal word is often worse than missing a secret if the output is intended for an LLM to "understand".
- **Visual Markers**: Clearly mark redacted sections (e.g., `[REDACTED_AWS_KEY]`).

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_in_place_replacement`**: Verify that `obfuscator.py` correctly replaces a secret at its exact offset within a larger string.
- **`test_overlapping_matches_handling`**: Ensure that if two regex rules match overlapping parts of the same string, the obfuscator correctly redacts the entire span without doubling the redaction.
- **`test_hashing_consistency`**: Assert that `obfuscate_hash("secret123")` always produces the same output in a single session.
- **`test_synthetic_data_generation`**: Assert that the replacement for a GitHub token looks like a GitHub token but is clearly fake.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Piped Obfuscation Output**
  - Given a file with "The AWS key is AKIA..."
  - When I run `cat file.txt | ./run.sh --obfuscate`
  - Then the output must be "The AWS key is AKIA... (redacted)"
  - And the non-secret text must be identical to the input.
- **Scenario: Hashed Obfuscation Mode**
  - When I obfuscate "token1" and "token1" with `--obfuscate-mode hash`
  - Then both occurrences should be replaced by the same hash string.
- **Scenario: Format Preservation in Redacted File**
  - Given a JSON file with secrets as values
  - When I obfuscate the file
  - Then the output should still be a valid JSON with the same structure, but the secret values redacted.
