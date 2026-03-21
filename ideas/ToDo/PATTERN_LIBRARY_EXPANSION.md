
## 0. Overview

This document defines the **architecture, taxonomy, ingestion workflow, and validation lifecycle** for the pattern library used by the **LLM Secrets Leak Detector**.

The system follows a **multi-engine detection approach** combining:

* Regex pattern matching
* Entropy analysis
* Contextual heuristics
* Rule-based classification

This hybrid model is considered industry standard for secret detection due to the limitations of regex-only approaches and entropy-only approaches ([wiz.io][1]).

---

## 1. Feature Alignment (UPDATED)

The pattern library must integrate seamlessly with the following **core detection capabilities**:

### 1.1 Detection Engine Compatibility

| Engine                | Role in Pattern System                              |
| --------------------- | --------------------------------------------------- |
| Regex (RE2)           | Primary matching engine for deterministic patterns  |
| Regex (Legacy)        | Handles complex/multiline patterns (e.g., PEM keys) |
| Entropy Analysis      | Validates randomness of extracted secrets           |
| Contextual Heuristics | Boosts/reduces confidence based on keywords         |
| Rule-based Logic      | Central rule registry (`rules.json`)                |

---

### 1.2 Detection Philosophy

The system follows a **multi-signal detection pipeline**:

```
Regex → Candidate Extraction
        ↓
Entropy → Randomness Validation
        ↓
Context → False Positive Reduction
        ↓
Scoring → Final Classification
```

This layered approach reduces false positives and improves recall compared to single-method scanners ([Gitea: Git with a cup of tea][2]).

---

## 2. Pattern Taxonomy (GLOBAL)

All patterns MUST map to one of the following classes:

```
data/
│
├── api_keys/
├── cloud_credentials/
├── database_credentials/
├── infrastructure/
├── authentication/
├── private_keys/
├── certificates/
├── tokens/
├── pii/
├── generic_secrets/
```

---

## 3. Directory Structure (UNCHANGED, ENFORCED)

Each class must contain:

```
data/<class_name>/
│
├── rules.json
├── regex.list
├── test_data.json
```

---

## 4. Rule Schema (UPDATED)

Expanded to support Feature Matrix capabilities:

```json
{
  "name": "mongodb_uri",
  "pattern": "mongodb(\\+srv)?:\\/\\/...",
  "engine": "re2",
  "severity": "high",
  "confidence": "high",
  "tags": ["database", "uri"],
  "keywords": ["mongodb", "db", "connection"],
  "entropy_required": true,
  "min_entropy": 4.0,
  "extract_groups": ["scheme", "user", "password", "host"],
  "redaction": "partial",
  "hashing": true
}
```

---

## 5. Detection Engines Integration

### 5.1 Regex Engines

| Engine         | Usage                                   |
| -------------- | --------------------------------------- |
| RE2            | Default (safe, linear time)             |
| Python `regex` | Fallback for multiline & advanced cases |

---

### 5.2 Entropy Engine

* Shannon entropy used for:

    * passwords
    * API keys
    * tokens

Typical thresholds:

| Type         | Threshold |
| ------------ | --------- |
| Base64       | ≥ 4.0     |
| Hex          | ≥ 3.0     |
| Alphanumeric | ≥ 4.0     |

Entropy is critical for detecting **unknown or proprietary secrets** ([Gitea: Git with a cup of tea][2]).

---

### 5.3 Contextual Heuristics

Boost detection if near:

```
password, secret, token, api_key, private_key, conn_string
```

Suppress detection if near:

```
example, test, dummy, localhost
```

---

## 6. Pattern Types (EXPANDED)

### 6.1 URI-Based Credentials (Super-URI)

Structure:

```
scheme://user:password@host:port/path?query
```

Supported:

* MongoDB (`+srv`)
* PostgreSQL
* MySQL
* Redis

---

### 6.2 Infrastructure Secrets

#### Kubeconfig

* `client-key-data`
* `token`

#### Terraform

```
access_key = "..."
secret_key = "..."
```

#### .env

Supports:

```
KEY=value
KEY="value"
export KEY=value
```

---

### 6.3 Private Keys

Multiline detection:

```
-----BEGIN ...-----
...
-----END ...-----
```

Handled by **legacy regex engine**.

---

## 7. Obfuscation Support (NEW)

Aligned with Feature Matrix:

| Type        | Detection                    |
| ----------- | ---------------------------- |
| Base64      | decode + entropy             |
| Hex         | decode + entropy             |
| URL Encoded | `%21`, `%40`, etc.           |
| Synthetic   | Faker-generated test secrets |

Modern scanners must detect **encoded secrets**, not just plain text ([GitHub][3]).

---

## 8. Import Pipeline (UPDATED)

### Step 1: Clone Sources

```bash
git clone https://github.com/advanced-security/secret-scanning-tools
git clone https://github.com/advanced-security/secret-scanning-custom-patterns
```

---

### Step 2: Extract Rules

Parse:

* YAML
* JSON
* Regex

---

### Step 3: Classification Mapping

| External  | Internal             |
| --------- | -------------------- |
| AWS       | cloud_credentials    |
| Mongo URI | database_credentials |
| PEM       | private_keys         |
| Slack     | api_keys             |

---

### Step 4: Normalize

Add:

* entropy flags
* keywords
* severity
* engine type

---

### Step 5: Deduplicate

* Hash regex
* Merge similar patterns

---

### Step 6: Generate Tests

Auto-create:

* Positive cases
* Negative cases
* Edge cases (low entropy)

---

## 9. Validation Pipeline (STRICT)

### 9.1 Unit Tests

* URI extraction
* entropy filtering
* multiline detection
* env parsing

---

### 9.2 Acceptance (BDD)

Examples:

#### MongoDB URI

```
mongodb+srv://admin:p@ssword123@cluster.mongodb.net
```

→ detect password

---

#### Private Key

```
-----BEGIN PRIVATE KEY-----
```

→ detect as private_key

---

### 9.3 Continuous Testing

After EVERY change:

```bash
pytest
```

Fix immediately.

---

## 10. Performance & Safety Alignment

| Feature           | Implementation     |
| ----------------- | ------------------ |
| Keyword Filtering | Aho-Corasick       |
| ReDoS Protection  | RE2 + timeouts     |
| Input Truncation  | 100k char limit    |
| Deduplication     | Longest match wins |

---

## 11. Reporting Integration

Patterns must support:

* Redaction
* Hashing
* Synthetic replacement

Output formats:

* Summary
* Short
* Full

---

## 12. Rule Quality Checklist

A rule is valid ONLY if:

* ✅ Has entropy logic (if needed)
* ✅ Has keywords
* ✅ Has test data
* ✅ Passes pytest
* ✅ No duplicates

---

## 13. False Positive Strategy

Main causes:

* weak regex
* missing entropy
* missing context

Mitigation:

1. Entropy thresholds
2. Context filters
3. Allowlist
4. Structural validation

False positives are a known major issue in secret scanners ([apiiro.com][4]).

---

## 14. Full Workflow

```
1. Clone repos
2. Extract rules
3. Classify
4. Normalize
5. Deduplicate
6. Generate tests
7. Run pytest
8. Fix issues
9. Commit
```

---

## 15. Future Enhancements

* LLM-based classification layer
* Secret verification via APIs
* Semantic code analysis
* Diff-based scanning

---

## 16. Key Takeaways

* Regex alone is insufficient
* Entropy alone is insufficient
* Context is mandatory

👉 Best results come from **combining all three signals**
