
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
