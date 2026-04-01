# Task: AI Security Firewall (LLM Gateway)

## 1. Objective & Context
*   **Goal**: Implement a proxy layer to intercept and scrub secrets from prompts before they reach LLM providers.
*   **Rationale**: This is the "killer feature" that differentiates the tool from traditional scanners by preventing leaks in real-time.
*   **Files Affected**:
    *   `app/api/proxy.py` (Gateway entry)
    *   `app/services/firewall.py` (Interception logic)
    *   `cli.py` (Optional local proxy mode)

## 2. Research & Strategy
*   **Architecture**: Reverse proxy for OpenAI/Anthropic APIs.
*   **Logic**: Intercept `messages` payload -> Scan content -> Redact/Block -> Forward to provider.
*   **Security**: Low-latency requirement is critical to avoid disrupting UX.

## 3. Implementation Checklist
- [ ] **Gateway Scaffolding**: Setup an Express/FastAPI proxy that handles streaming requests.
- [ ] **Request Interception**: Parse standard LLM request formats (OpenAI-compatible).
- [ ] **Scrubbing Engine**: Apply `detector.py` and `obfuscator.py` to prompt text.
- [ ] **Policy Enforcement**: Implement "Block" vs "Redact" modes based on risk score.
- [ ] **Response Mirroring**: Ensure streaming responses from the LLM are passed back to the client transparently.
- [ ] **Logging & Auditing**: Log redacted prompts for security admin review (without sensitive data).

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test proxy logic with mocked LLM endpoints.
- [ ] Benchmark the overhead added by the scanning layer (Target < 50ms).

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: User sends a prompt with an AWS key to the proxy; the key is redacted before reaching OpenAI.
- [ ] **Scenario**: A "CRITICAL" prompt (e.g., system prompt injection + secrets) is blocked entirely.
- [ ] **Scenario**: Streaming response from the LLM is delivered to the user with no noticeable lag.

## 5. Demo & Documentation
- [ ] **demo.sh**: Add a section demonstrating the "Firewall" mode with a sample API call.
- [ ] **README.md**: Add documentation on how to point OpenAI/LangChain clients to the local/SaaS gateway.

## 6. Engineering Standards
*   **Performance**: Use zero-copy buffers where possible for high-throughput proxying.
*   **Privacy**: Ensure the proxy itself doesn't become a point of data leakage; logs must be rigorously scrubbed.
