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
7. Run pytest[PATTERN_LIBRARY_EXPANSION.md](PATTERN_LIBRARY_EXPANSION.md)
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
