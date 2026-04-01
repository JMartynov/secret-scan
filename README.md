# LLM Secrets Leak Detector

**LLM Secrets Leak Detector** is a security tool designed to prevent accidental exposure of sensitive data when interacting with Large Language Models (LLMs).

Modern AI development workflows frequently involve sending code snippets, configuration files, logs, and debugging output to language models. In many cases developers unintentionally include sensitive information such as API keys, database credentials, private tokens, or internal infrastructure details.

This project detects those secrets **before they leave the developer’s environment**.

The system scans prompts, responses, logs, and source code to identify potential secrets and warns the user when confidential data may be exposed.

---

# Problem

LLM-assisted development has dramatically increased developer productivity. However, it also introduced a new security risk.

Developers regularly paste entire code blocks, configuration files, or logs into AI assistants to ask questions like:

> “Here is my code, can you help debug it?”

These inputs often contain secrets such as:

* API keys
* database credentials
* private tokens
* authentication secrets
* internal infrastructure URLs
* encryption keys
* JWT tokens

Example input that might be leaked:

```
OPENAI_API_KEY=sk-abc123
DATABASE_URL=postgres://user:pass@db
JWT_SECRET=super-secret-token
```

Once sent to an external LLM service, this data may:

* appear in provider logs
* be stored for debugging
* violate compliance policies
* leak sensitive infrastructure details

The exposure of secrets in software artifacts has been increasing rapidly, with millions of credentials discovered in public repositories in recent years. ([arXiv][1])

Security teams now treat **secret detection as a critical part of modern development pipelines**.

---

# Solution

LLM Secrets Leak Detector automatically scans AI interaction data and identifies potential secrets before they are transmitted.

The tool analyzes:

* prompts sent to LLMs
* LLM responses
* application logs
* code snippets
* configuration files

When a potential secret is detected, the tool generates a warning describing:

* the secret type
* location
* severity level

Example output:

```
⚠ Secrets detected

Type: OpenAI API Key
Location: line 3
Risk: HIGH

Type: Database credentials
Location: line 4
Risk: CRITICAL
```

This allows developers to **remove or redact sensitive information before it reaches an external AI system.**

---

# Core Detection Approach

The detection engine uses a layered strategy similar to modern secret detection systems.

Most secret scanners rely on three complementary techniques:

1. **Pattern Matching (Regex)**
   Identifies secrets with known formats such as AWS keys or GitHub tokens.

2. **Entropy Analysis**
   Detects strings that appear random, which is typical for cryptographic tokens.

3. **Contextual Analysis**
   Reduces false positives by analyzing surrounding code and variable names. ([gitguardian.com][2])

Combining these methods significantly improves accuracy.

---

# Secret Types Detected

The scanner detects over **180 classes** of sensitive data, including:

### API Keys

Examples:

```
sk-xxxxxxxxxxxxxxxx
AIzaSyxxxxxxxxxxxx
```

### Cloud Credentials

Examples:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AZURE_TOKEN
```

### Version Control Tokens

Examples:

```
ghp_xxxxxxxxxxxxxxxxx
glpat_xxxxxxxxxxxxx
```

### Authentication Secrets

Examples:

```
JWT_SECRET
SESSION_SECRET
PRIVATE_KEY
```

### Database Credentials

Examples:

```
postgres://user:password@host
mysql://root:pass@db
```

### Cryptographic Material

Examples:

```
-----BEGIN PRIVATE KEY-----
```

---

# Feature Matrix

The **LLM Secrets Leak Detector** provides a comprehensive suite of features designed for security, performance, and developer experience.

| Category | Feature | Status | Implementation Details |
| :--- | :--- | :--- | :--- |
| **Detection Engines** | **Regex Matching (RE2)** | ✅ | Primary engine using `google-re2`.<br>Fast, linear-time matching. |
| | **Regex Matching (Legacy)** | ✅ | Fallback to `regex` (Python) for complex patterns.<br>ReDoS protection. |
| | **Entropy Analysis** | ✅ | Shannon entropy scoring for random-looking tokens (min 20 chars). |
| | **Contextual Heuristics** | ✅ | Identifies secrets based on surrounding keywords like `prod`, `password`, `key`. |
| | **Rule-based Logic** | ✅ | 1750+ rules loaded from `data/` (Expanded 2026). |
| **Input Sources** | **File Scanning** | ✅ | Scans local files with UTF-8 support.<br>Error handling. |
| | **Stdin / Piped Input** | ✅ | Real-time processing of piped data (e.g., `cat log \| ./run.sh`). |
| | **Direct Text** | ✅ | Via `--text` flag for quick prompt validation. |
| | **Streaming** | ✅ | Optimized line-by-line generator for low-latency processing. |
| **Obfuscation** | **Redact** | ✅ | Masks the middle of secrets (e.g., `AKIA...CDEF`). |
| | **Hash** | ✅ | Consistent SHA-256 hashing (first 12 chars) for safe debugging. |
| | **Synthetic** | ✅ | [NEW] Realistic fake data generation (AWS, GitHub, Emails) using `Faker`. |
| **Safety & Performance** | **Keyword Filtering** | ✅ | Uses `Aho-Corasick` automaton to skip rules missing their required keywords. |
| | **Parallel Scanning** | ✅ | [NEW] Utilizes `ProcessPoolExecutor` for high-speed historical audits. |
| | **Commit Caching** | ✅ | [NEW] Incremental scanning using `.secretscan_cache` to skip verified SHAs. |
| | **ReDoS Protection** | ✅ | `SIGALRM` timeouts (1s) for non-RE2 regex execution. |
| | **Input Truncation** | ✅ | Blocks capped at 100,000 characters to prevent memory exhaustion. |
| | **Deduplication** | ✅ | Merges overlapping findings.<br>Prioritizes longest matches. |
| | **Force All Scan** | ✅ | `--force-scan-all` bypasses keyword filters so every line is scored. |
| **Reporting & UI** | **Surgical Highlighting** | ✅ | [NEW] ANSI-colored context lines with the secret highlighted in red. |
| | **Remediation Hints** | ✅ | [NEW] Actionable advice with links to official provider documentation. |
| | **Colorized Output** | ✅ | ANSI colors for risk levels (Red=High, Yellow=Medium, Blue=Low). |
| | **Report Formats** | ✅ | `Summary` (counts only).<br>`Short` (redacted).<br>`Full` (raw secrets + context).<br>`SARIF` (GitHub Code Scanning). |
| | **CI/CD Friendly** | ✅ | `--nocolors` flag.<br>Standard exit codes for automation. |
| **Testing & Dev** | **BDD Acceptance** | ✅ | 25 scenarios in `acceptance.feature` (including Git workflows) using `pytest-bdd`. |
| | **Performance Bench** | ✅ | [NEW] Automated suite to verify caching and parallelization gains. |
| | **Unit Testing** | ✅ | Comprehensive suite for core logic (detector, obfuscator, cli). |
| | **Synthetic Corpus** | ✅ | `generate_test_data.py` creates a balanced test set from rules. |
| | **Rule Deduplication** | ✅ | `tools/deduplicate_rules.py` keeps the catalog clean before release. |

## Git & CI/CD Integration

The detector is now natively aware of Git lifecycles, allowing for surgical scans of changes rather than entire files.

### 🛠 Git Scanning Modes

```bash
# Scan staged changes (perfect for pre-commit hooks)
./run.sh --git-staged --mode fast

# Scan unstaged changes in the working directory
./run.sh --git-working

# Scan the diff between a feature branch and main (PR audits)
./run.sh --git-branch origin/main --format sarif

# Deep audit of repository history (Parallelized & Cached)
./run.sh --history --since "1 month ago" --max-commits 100
```

### 🏎 Performance & Scalability

- **Parallel Execution**: Large-scale historical audits automatically utilize multiple CPU cores for regex and entropy analysis.
- **Commit Caching**: The engine maintains a `.secretscan_cache` to track verified "clean" commits, reducing redundant scan times by up to 90% in incremental audits.
- **Modes**: Choose between `fast` (optimized for <1s hooks), `balanced` (standard dev), and `deep` (thorough CI audits).

---

## Surgical Highlighting & Remediation

When a secret is detected, the terminal output provides immediate visual context and actionable fix instructions.

```text
⚠ Secrets detected: 1
- HIGH: 1

Type: stripe_api_key
Location: line 1
Risk: HIGH
Suggestion: Rotate this Stripe API key immediately in your dashboard. See: https://stripe.com/docs/keys#api-key-rotation
Context: config process result Stripe secret: [SECRET_HIGHLIGHTED_IN_RED]
```

Remediation hints now include direct links to official security guides for AWS, GitHub, Stripe, and Google Cloud to guide developers through the revocation and rotation process.

---

## Extended Infrastructure Mode

The latest feature expansion brings the infrastructure-focused taxonomy front and center:

* `data/infrastructure` now houses rules for credit cards, IBANs/SEPA references, national ID numbers, and other high-risk identifiers.
* Entropy-aware scoring plus overlap resolution lets structured infrastructure matches win over generic keywords or high-entropy heuristics.
* The CLI `--force-scan-all` option ensures legacy logs that omit keywords still get evaluated (see the new acceptance scenario for this mode).
* Dedicated tests cover deduped rules, synthetic obfuscation, and the expanded dataset to ensure the library stays precise.

## Development Utilities

Keep the catalog healthy with the accompanying tools:

* `tools/migrate_patterns.py` normalizes schema fields, adds entropy defaults, and maps external categories to the in-tree taxonomy.
* `tools/generate_test_data.py` rebuilds the base64-encoded `data/*/test_data.json` files from regexes so every rule ships with reproducible samples.
* `tools/deduplicate_rules.py` merges duplicate patterns across categories before rules ship.
* Use `tools/regex_lint.py`, `tools/run_safe_regex.py`, and `tools/run_redoctor.py` to guard against ReDoS, syntax drift, and schema regressions.

Run `pytest tests/test_acceptance.py::test_force_scan_keywordless` before releasing to exercise the keywordless mode.

---

# Pattern Database

The detection engine can leverage large open-source pattern databases containing thousands of secret signatures.

For example, open datasets include **over 1600 regular expressions** that detect API keys, tokens, passwords, and other credentials across hundreds of services. ([GitHub][3])

This allows the scanner to stay updated with newly introduced API key formats.

---

# Project Goals

The project focuses on **protecting AI workflows** rather than traditional repository scanning.

Key design goals:

### AI-first security

Detect secrets inside:

* LLM prompts
* chat transcripts
* agent logs
* debugging sessions

### Developer-first experience

The tool integrates directly into developer workflows without requiring complex configuration.

### Local processing

All scanning occurs locally to ensure no data leaves the environment.

### Fast feedback

Secrets should be detected immediately during development.

---

# Core Components

The system is composed of several modules.

### Detection Engine

Responsible for identifying potential secrets using:

* regex pattern matching
* entropy scoring
* context heuristics

### Pattern Database

A continuously updated collection of secret signatures.

Includes patterns for:

* API providers
* cloud platforms
* CI/CD tokens
* authentication systems

### Scanner Interface

The scanner processes different input sources:

* text prompts
* log streams
* source files
* application outputs

### Reporting System

Findings are returned as structured results including:

* secret type
* location
* confidence score
* risk level

---

# Architecture

The architecture prioritizes simplicity and speed.

```
Input Sources
    │
    │
    ▼
Preprocessing Layer
    │
    │
    ▼
Detection Engine
    ├── Regex Matching
    ├── Entropy Detection
    └── Context Analysis
    │
    ▼
Secret Classification
    │
    ▼
Security Report
```

---

# Example Detection

Input text:

```
Here is my configuration:

DATABASE_URL=postgres://admin:password@localhost
```

Output:

```
Secrets detected:

[1] OpenAI API Key
location: line 3
risk: HIGH

[2] Database Credentials
location: line 4
risk: CRITICAL
```

---

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
./run.sh example_file.txt
```

Or scan text directly:
```bash
# Standard scan
python3 cli.py --text "My API key is AIzaSy-12345"

# Force scan all lines (bypasses keyword filters)
python3 cli.py --force-scan-all .
```

### Data Obfuscation & Masking

You can redact sensitive data from logs or prompts while preserving the rest of the text. This is useful for sanitizing data before sharing it with an LLM or for safe debugging.

Enable obfuscation with the `--obfuscate` flag:

```bash
# Default mode: redact (Redacts middle of the secret)
# Input: "My key is ghp_1234567890abcdefghijklmnopqrstuvwx"
# Output: "My key is ghp_...uvwx"
cat logs.txt | python3 cli.py --obfuscate
```

Choose different obfuscation strategies with `--obfuscate-mode`:

#### 1. `redact` (Default)
Partial masking that keeps the prefix/suffix for context but hides the sensitive core.
* **Example:** `AKIA...CDEF`

#### 2. `hash`
Replaces secrets with a consistent, short SHA-256 hash. Identical secrets will result in identical hashes, which is crucial for debugging data flows without seeing the actual values.
* **Example:** `[HASHED_d8c7b92f4a19]`

#### 3. `synthetic` (Recommended for LLM Prompts)
Replaces secrets with realistic-looking fake data that matches the original format (using the `Faker` library). This allows LLMs to still "understand" the structure of your data (e.g., seeing a fake AWS key where a real one was) without exposing real credentials.
* **Example (AWS ID):** `AKIAJ7O2N6M4L9K0P8R1`
* **Example (GitHub Token):** `ghp_zXyWvUtSrQpOnMlKjIhGfEdCbA9876543210`
* **Example (Email):** `fake_user@example.org`

```bash
# Use synthetic mode for realistic placeholders
./run.sh --obfuscate --obfuscate-mode synthetic logs.txt
```

### Custom CLI helpers

The repository ships with a few convenience commands:

* `./run.sh <file>` formats and scans a local file with `cli.py` and prints the report.
* `python3 cli.py --text "<string>"` runs the scanner on an inline string (useful when building prompts before sending them to an LLM).
* `python tools/generate_test_data.py` rebuilds `data/test_data.json` from `data/rules.json` and should be rerun whenever the rule set changes.

## Usage Example

```
$ ./run.sh test_file.py

⚠ Secrets detected: 1
- CRITICAL: 1

Type: Database Credentials
Location: line 10
Risk: CRITICAL
Content: post...ocal (redacted)
```

# Test Data & Custom Cases

Every rule in `data/rules.json` maps to a base64-encoded positive and negative sample under `data/test_data.json`. `tools/generate_test_data.py` drives the data:

* It loads each regex, runs it through `exrex` (with length caps) to emit matches, and encodes them so the detector tests operate on identical strings as production data.
* Negatives are hand-crafted near-misses that resemble real-world secrets but should not trigger a hit.
* Rules listed in `STRICT_RULES` bypass the default `encode_str` mutation because even inserting `DUMMY_IGNORE` would break the required format.
* Custom helpers generate valid payloads for the trickiest patterns (`auth0_domain_url`, `skybiometry_api_key`, `okta_api_domain_url`, `facebook_oauth_id`, `linemessaging_api_key`, `nethunt_api_key`) so the detector still sees legal samples even though those regexes restrict character sets or lengths tightly.

Run `python tools/generate_test_data.py` after any rule changes; it prints progress every 100 rules and overwrites `data/test_data.json` with the refreshed corpus that powers the pytest suite.


# Use Cases

### AI Application Development

Developers building:

* chatbots
* RAG pipelines
* AI agents
* coding assistants

can scan prompts before sending them to LLM APIs.

---

### Security Auditing

Security teams can analyze:

* prompt logs
* application logs
* LLM interaction history

to ensure no secrets were exposed.

---

### Compliance

Organizations can enforce policies preventing sensitive information from being sent to external AI providers.

---

### DevSecOps Integration

The scanner can be integrated into:

* CI/CD pipelines
* AI gateways
* API proxies
* developer tooling

---

# Target Users

### AI Developers

Engineers building LLM-powered applications.

### Security Engineers

Teams responsible for application security reviews.

### AI Startups

Companies working with prompt engineering and LLM pipelines.

---

# Roadmap

The project evolves in several stages.

### CLI Scanner

A lightweight command-line tool for scanning prompts and logs.

### API Service

A service that allows AI systems to validate prompts before sending them to LLM providers.

### Developer Tooling

Integration with:

* IDE plugins
* Git hooks
* CI pipelines

### Enterprise Security Platform

Future capabilities may include:

* real-time prompt filtering
* AI data loss prevention (DLP)
* secret monitoring across AI infrastructure

---

# Why This Matters

AI-assisted development dramatically increases the speed of coding and debugging, but it also increases the risk of accidentally exposing sensitive data.

Developers frequently paste large blocks of code or logs into AI systems without reviewing them for secrets.

LLM Secrets Leak Detector provides a safety layer that prevents confidential data from leaving the organization.

---

# License

MIT License


[1]: https://arxiv.org/abs/2307.00714?utm_source=chatgpt.com "A Comparative Study of Software Secrets Reporting by Secret Detection Tools"
[2]: https://www.gitguardian.com/solutions/secrets-detection?utm_source=chatgpt.com "Secrets Detection: Scan Code for Exposed API Keys and Credentials | GitGuardian"
[3]: https://github.com/mazen160/secrets-patterns-db?utm_source=chatgpt.com "GitHub - mazen160/secrets-patterns-db: Secrets Patterns DB: The largest open-source Database for detecting secrets, API keys, passwords, tokens, and more."
