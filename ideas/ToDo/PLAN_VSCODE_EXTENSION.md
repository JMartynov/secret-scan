# Task: VSCode Extension for Real-time Scanning

## 1. Objective & Context
*   **Goal**: Create a VSCode extension to scan code and prompts in the editor in real-time.
*   **Rationale**: To catch secrets during development, even before a commit is made, providing the ultimate shift-left security.
*   **Files Affected**:
    *   `extensions/vscode/` (New project)
    *   `extensions/vscode/src/extension.ts` (Logic)

## 2. Research & Strategy
*   **Engine**: Use the WASM-compiled version of RE2 or call the local CLI/API.
*   **UX**: Highlight detected secrets with squiggly lines (Diagnostics) and provide "Quick Fix" actions.
*   **Distribution**: Publish to the VSCode Marketplace.

## 3. Implementation Checklist
- [ ] **Extension Scaffolding**: Setup the VSCode extension project with TypeScript.
- [ ] **Live Document Scanning**: Trigger scans on text changes (`onDidChangeTextDocument`).
- [ ] **Diagnostics**: Show findings in the "Problems" tab and as inline decorations.
- [ ] **Redaction Quick Fix**: Add a "Redact Secret" action that automatically replaces the match with a placeholder.
- [ ] **Configuration**: Add settings for API keys, custom rules, and PII toggle.
- [ ] **Paste Interception**: Specifically check text when it's pasted into the editor.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] Test the scanning logic within the VSCode extension host environment.
- [ ] Verify that decorations are correctly positioned on multi-line matches.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Developer pastes an OpenAI key; a warning appears immediately.
- [ ] **Scenario**: Developer clicks "Redact", and the key is replaced by `[REDACTED]`.
- [ ] **Scenario**: Large files do not cause the editor to lag during scanning.

## 5. Demo & Documentation
- [ ] **Marketplace Page**: Create an attractive README with screenshots and a video demo.
- [ ] **Quickstart**: Add an onboarding walkthrough within the extension.

## 6. Engineering Standards
*   **Performance**: Use debouncing to ensure scanning doesn't impact typing performance.
*   **Privacy**: Process data locally by default; only use the API if explicitly enabled by the user.
