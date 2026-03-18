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
