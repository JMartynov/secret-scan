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

For example:

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

The scanner detects many classes of sensitive data, including:

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

OPENAI_API_KEY=sk-test1234567890
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

# Set API key
export OPENAI_API_KEY="your-key"

# Run
python3 infinite_memory_chat.py
```

Or simply:
```bash
chmod +x run.sh
export OPENAI_API_KEY="your-key"
./run.sh
```

## Configuration

### Quick Start (OpenAI Backend)

1. **Create a `.env` file:**
```bash
cp env.example .env
```

2. **Add your OpenAI API key:**
```bash
VECTOR_BACKEND=openai
OPENAI_API_KEY=your_openai_api_key_here
```

3. **Run the application:**
```bash
./run.sh
```

## Usage Example

```
You: My name is Alice and I'm working on Project Neptune.
Assistant: Nice to meet you, Alice! I will remember that...


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
