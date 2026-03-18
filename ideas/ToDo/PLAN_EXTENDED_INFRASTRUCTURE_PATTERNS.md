# PLAN: Extended Technical Patterns (URI, DB, Infrastructure)

## 1. Objective
Expand the pattern library to cover complex infrastructure credentials and connection strings commonly found in developer prompts.

## 2. Analogs & Research
- **Iana Service Names**: Reference for standard port/scheme mappings.
- **ConnectionStrings.com**: Resource for various DB connection formats.

## 3. Implementation Details

### 3.1 Enhanced URI Regex
Implement a "Super-URI" pattern that captures the common structure:
`[scheme]://[user]:[password]@[host]:[port]/[path]?[query]`

Specific focuses:
- **MongoDB**: `mongodb(\+srv)?://` (Handles SRV records).
- **PostgreSQL/MySQL**: Standardizes the credential extraction.
- **Redis**: Handles the `redis://:password@host` format where the user is often omitted.

### 3.2 Cloud Infrastructure
- **Kubeconfig**: Patterns for certificates and tokens inside YAML blocks.
- **Terraform/HCL**: Detect `access_key` and `secret_key` assignments in HCL syntax.
- **Environment Files**: Robust `.env` parsing that handles quotes and exports.

### 3.3 Private Keys & Certificates
- Detect multi-line headers:
    - `-----BEGIN RSA PRIVATE KEY-----`
    - `-----BEGIN OPENSSH PRIVATE KEY-----`
- Capture the entire block until the `END` footer.

## 4. Best Practices
- **Entropy for Passwords**: URIs like `postgres://admin:password@localhost` are often false positives. Apply entropy checks to the `password` group specifically.
- **Non-Greedy Capture**: Ensure the `password` group stops at the `@` or `:` symbols.
- **Encoding Awareness**: Detect secrets in URL-encoded formats (e.g., `%21` for `!`).

---

## 5. Testing Strategy

### 5.1 Unit Tests (`pytest`)
- **`test_uri_component_extraction`**: Verify that the "Super-URI" regex correctly maps to named groups (scheme, user, password, host).
- **`test_multiline_cert_matching`**: Assert that `detector.py` can capture a 20-line PEM file as a single finding.
- **`test_mongodb_srv_detection`**: Specifically test the `+srv` variant of MongoDB URIs.
- **`test_env_file_parser`**: Test `.env` formats: `KEY="val"`, `export KEY=val`, `KEY=val # comment`.

### 5.2 Acceptance Tests (BDD)
- **Scenario: Complex MongoDB URI Detection**
  - When I scan "mongodb+srv://admin:p@ssword123@cluster0.mongodb.net/test?retryWrites=true"
  - Then it should report "database_credentials" for "p@ssword123"
- **Scenario: Private Key Block Detection**
  - Given a block starting with `-----BEGIN PRIVATE KEY-----` and ending with `-----END PRIVATE KEY-----`
  - When I scan the block
  - Then it should be detected as "private_key"
- **Scenario: Infrastructure-in-Context**
  - When I scan "Here is my kubeconfig: client-key-data: dGhpcyBpcyBhIGZha2UgdG9rZW4="
  - Then the Base64 token should be identified as a "Potential Secret".
