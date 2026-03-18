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
