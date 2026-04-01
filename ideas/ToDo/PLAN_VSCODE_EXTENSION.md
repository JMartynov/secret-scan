# Task: VSCode Extension for Real-time Scanning

## 1. Objective & Context
*   **Goal**: Create a VSCode extension to scan code and prompts in the editor in real-time as the developer types.
*   **Rationale**: Provides the ultimate "shift-left" security by catching leaks before they are even saved to disk or committed to git.
*   **Files Affected**:
    *   `extensions/vscode/`: New TypeScript project.
    *   `extensions/vscode/src/extension.ts`: Core extension logic.
    *   `extensions/vscode/src/scanner.ts`: Interface to the local CLI or API.

## 2. Research & Strategy
*   **Mechanism**: Use `vscode.DiagnosticCollection` to highlight secrets with squiggly lines.
*   **Logic**: Run scans on `onDidChangeTextDocument` with a 500ms debounce.
*   **Engine Choice**: Call the local `cli.py` or use a WASM-compiled version of the engine for zero-latency local scans.

## 3. Implementation Checklist
- [ ] **Extension Scaffold**: Setup the VSCode extension project with standard security permissions.
- [ ] **Live Squiggles**: Implement `Diagnostic` providers to highlight secrets directly in the editor.
- [ ] **Quick Fixes**: Add "Redact this secret" and "Ignore this secret" (adds to baseline) actions.
- [ ] **StatusBar Indicator**: Show a real-time "Security Status" in the VSCode status bar.
- [ ] **Configuration UI**: Add a settings page for API keys, scanning modes (Fast/Balanced/Deep), and PII toggles.

## 4. Testing & Verification (Mandatory)
### 4.1 Unit Testing
- [ ] `test_decoration_mapping`: Verify that sqwigglies align correctly with the secret's start/end offsets.
- [ ] `test_debounce_logic`: Assert that scanning doesn't trigger on every single keystroke.

### 4.2 Acceptance Testing (BDD)
- [ ] **Scenario**: Developer pastes a secret (Warning appears instantly).
- [ ] **Scenario**: Developer clicks "Redact" (Secret is replaced by a placeholder).
- [ ] **Scenario**: False Positive Management (Developer clicks "Ignore", squiggle disappears).

### 4.3 Test Data Obfuscation
- [ ] Use the standard `tests/data/test_data.json` for extension testing.

## 5. Demo & Documentation
- [ ] **Marketplace Page**: Create high-quality screenshots and a GIF showing the "Redact" quick-fix.
- [ ] **README.md**: Document how to connect the extension to a private SaaS instance.

## 6. Engineering Standards
*   **Tone**: Senior Engineer.
*   **Perf**: Absolute priority on UI responsiveness; scanning must run in a background worker.
*   **Security**: The extension must never upload full files to the cloud without explicit user consent.
