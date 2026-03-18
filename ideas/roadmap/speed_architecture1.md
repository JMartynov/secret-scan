Designing a **large regex-based secret database (400–1500 patterns)** safely in Python requires preventing **catastrophic backtracking**, which can freeze your scanner when certain patterns interact with malicious input (ReDoS). Catastrophic backtracking occurs when regex engines repeatedly retry many matching paths—often caused by **nested quantifiers like `(a+)+`** or ambiguous repetitions. ([| Help Center][1])

Below is a **practical architecture for Python secret-pattern databases** used in scanners, adapted for your LLM-prompt detector.

---

# 1. The main cause of ReDoS in secret scanners

Typical dangerous patterns:

```regex
(.*)+
(a+)+
(\w+)*\d
```

Example bad regex:

```regex
^(a+)+$
```

Input:

```
aaaaaaaaaaaaaaaaaaaaab
```

This causes exponential backtracking and huge CPU usage. ([| Help Center][1])

Secret scanners are vulnerable because:

```
500+ regex rules
×
large prompt text
×
multiple matches
```

---

# 2. Architecture for a safe regex secret database

Recommended architecture:

```
Secret Pattern DB
   │
   ├── Safe regex rules
   ├── Keyword filters
   ├── Entropy detector
   ├── Precompiled regex pool
   └── Safe regex engine
```

Important principle:

```
never run regex blindly
```

---

# 3. Design rule #1 — Safe regex style guide

When building your secret-pattern database, enforce **safe regex rules**.

### NEVER allow

```
(a+)+
(a*)*
(.+)+
(.*)*
```

These create nested repetition.

Instead rewrite.

### Example

Bad:

```
(api.*key)+
```

Good:

```
api[^ \n]{0,50}key
```

---

### Replace greedy wildcards

Bad:

```
.*token.*
```

Good:

```
[^\n]{0,200}token[^\n]{0,200}
```

Why:

```
.* can scan entire document
```

---

### Avoid overlapping patterns

Bad:

```
(a|aa)+
```

Better:

```
a+
```

---

# 4. Design rule #2 — Require keyword filters

Regex rules should **only run when a keyword appears**.

Example rule:

```python
{
 "name": "github_token",
 "keywords": ["github", "token", "ghp"],
 "regex": r"ghp_[A-Za-z0-9]{36}"
}
```

Execution pipeline:

```
if keyword found:
    run regex
```

This reduces regex runs by **90–99%**.

---

# 5. Design rule #3 — Compile regex once

Never compile regex dynamically.

Bad:

```python
for pattern in patterns:
    re.search(pattern, text)
```

Good:

```python
compiled = [re.compile(p) for p in patterns]

for regex in compiled:
    regex.search(text)
```

Compiling once improves performance significantly when patterns are reused. ([peerdh.com][2])

---

# 6. Design rule #4 — Limit input size

Before regex scanning:

```python
MAX_TEXT = 100000

text = text[:MAX_TEXT]
```

This protects against:

```
10MB logs pasted into prompts
```

Also split scanning:

```
scan line by line
scan tokens
scan chunks
```

---

# 7. Design rule #5 — Timeouts for regex

Python’s `re` module has **no built-in timeout**.

Implement one.

Example:

```python
import signal
import re

def safe_search(pattern, text):
    def handler(signum, frame):
        raise TimeoutError()

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(1)

    try:
        return re.search(pattern, text)
    finally:
        signal.alarm(0)
```

This prevents runaway regex.

---

# 8. Design rule #6 — Use RE2-style engines when possible

Backtracking engines cause ReDoS.

Safer engines:

* Google **RE2**
* Rust regex
* Hyperscan

They run in **linear time**.

Example Python bindings:

```
re2
pyre2
```

These engines **remove catastrophic backtracking entirely**. ([Medium][3])

Example:

```python
import re2

pattern = re2.compile(r"ghp_[A-Za-z0-9]{36}")
pattern.search(text)
```

---

# 9. Design rule #7 — Static regex linting

Before adding a rule to your database:

Run a tool like:

* `regexploit`
* `safe-regex`
* `vuln-regex-detector`

These tools test regexes for catastrophic backtracking and generate attack strings. ([PyPI][4])

Workflow:

```
new regex rule
    ↓
run safety checker
    ↓
approved pattern
    ↓
added to database
```

---

# 10. Recommended rule schema

Example JSON rule format:

```json
{
 "id": "openai_api_key",
 "category": "api_key",
 "keywords": ["openai", "api", "key"],
 "regex": "sk-[A-Za-z0-9]{20,}",
 "entropy": 3.5,
 "risk": "high"
}
```

---

# 11. Fast scanning algorithm

Recommended scanning pipeline:

```
text
 │
 ▼
split into lines
 │
 ▼
keyword filter
 │
 ▼
regex detection
 │
 ▼
entropy check
 │
 ▼
secret classification
```

This avoids running **500 regex patterns on every line**.

---

# 12. Example safe Python scanner architecture

```python
import re

class SecretScanner:

    def __init__(self, rules):
        self.rules = []
        for r in rules:
            self.rules.append({
                "regex": re.compile(r["regex"]),
                "keywords": r["keywords"],
                "name": r["name"]
            })

    def scan(self, text):
        findings = []

        for line_num, line in enumerate(text.splitlines(), 1):

            for rule in self.rules:
                if not any(k in line for k in rule["keywords"]):
                    continue

                if rule["regex"].search(line):
                    findings.append((rule["name"], line_num))

        return findings
```

---

# 13. Realistic performance expectations

For a **500-rule database**:

```
keyword filtering
+ compiled regex
+ line scanning
```

You can scan:

```
~5–20 MB text/sec
```

on a normal laptop.

---

# 14. Biggest mistake in secret scanners

Many implementations do:

```
for regex in 500_patterns:
    re.search(regex, entire_prompt)
```

This is slow and vulnerable.

Instead:

```
keyword → regex
```

---

# 15. Best architecture for your project

For your **LLM Secrets Leak Detector** I recommend:

```
Secret Pattern DB
   ├── structured secrets (regex)
   ├── infrastructure secrets
   ├── entropy detector
   └── LLM context patterns
```

With runtime safety:

```
keyword filtering
regex compilation
regex linting
input limits
timeout protection
```

---

✅ **My strongest recommendation**

If you expect **500–1000 regex patterns**, use:

```
RE2 (pyre2)
```

instead of Python `re`.

That completely removes catastrophic backtracking.

---

If you want, I can also show a **very powerful trick used in high-performance secret scanners**:

**How to convert hundreds of regex patterns into a single Aho-Corasick automaton so your scanner becomes ~20-50× faster than normal regex scanning.**

[1]: https://help.fluidattacks.com/portal/en/kb/articles/criteria-fixes-python-211?utm_source=chatgpt.com "Asymmetric denial of service - ReDoS - Python"
[2]: https://peerdh.com/blogs/programming-insights/regex-performance-optimization-techniques-in-python-1?utm_source=chatgpt.com "Regex Performance Optimization Techniques In Python – peerdh.com"
[3]: https://medium.com/%40sohail_saifi/why-your-regex-will-eventually-crash-your-production-server-with-real-horror-stories-fa10eea56ec9?utm_source=chatgpt.com "Why Your Regex Will Eventually Crash Your Production Server (With Real Horror Stories) | by Sohail Saifi | Medium"
[4]: https://pypi.org/project/regexploit/?utm_source=chatgpt.com "regexploit · PyPI"
