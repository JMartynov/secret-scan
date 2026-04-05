# Task: GitHub Marketplace Publication & Action CD

## 1. Objective & Context
*   **Goal**: Publish the `secret-scan` GitHub Action to the GitHub Marketplace and automate its updates.
*   **Rationale**: Makes it easy for developers to integrate secret scanning directly into their existing GitHub CI/CD pipelines.
*   **Target**: [GitHub Marketplace (Actions)](https://github.com/marketplace?type=actions) as `Secret Scan Action`.

## 2. Research & Strategy
*   **Action Type**: Use a `composite` or `docker` action for portability.
*   **Versioning**: Automate major version tags (e.g., `v1`) to point to the latest minor version for user convenience.
*   **Marketplace Metadata**: Use `action.yml` to define icons, branding, and inputs/outputs.

## 3. Implementation Checklist
- [ ] **Initial Setup**:
    - [ ] Create `action.yml` in the root directory.
    - [ ] Define inputs (e.g., `path`, `force-scan`, `obfuscation-mode`) and outputs.
    - [ ] Design branding (icon and color) for the Marketplace listing.
    - [ ] Manually create the first release (e.g., `v1.0.0`) and check "Publish to Marketplace".
- [ ] **Automated CD (GitHub Action)**:
    - [ ] Create `.github/workflows/marketplace-release.yml`.
    - [ ] Configure it to trigger on new tags (e.g., `v*`).
    - [ ] Implement logic to automatically update major version tags (e.g., move `v1` tag to point to `v1.2.3`).
    - [ ] Automate the generation of GitHub Releases with a summary of changes.

## 4. Testing & Verification
- [ ] **Local Integration Test**: Use the action in a test workflow `.github/workflows/verify-action.yml` within the `secret-scan` repo itself.
- [ ] **Cross-Repo Test**: Create a dedicated test repository and use the action via its full path (`JMartynov/secret-scan@v1`).

## 5. Engineering Standards
*   **Versioning**: Maintain both fixed tags (`v1.2.3`) and rolling tags (`v1`, `v1.2`).
*   **Compatibility**: Ensure the action remains compatible with major GitHub Actions runner environments (Ubuntu, macOS, Windows).
*   **Minimalism**: The action should be fast and have minimal setup overhead.
