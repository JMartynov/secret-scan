# Task: PyPI Publication & CD Automation

## 1. Objective & Context
*   **Goal**: Enable public installation of `secret-scan` via `pip` and automate updates on every repository change.
*   **Rationale**: Standardizes distribution and ensures users always have the latest, most secure version of the detector.
*   **Target**: [PyPI (Python Package Index)](https://pypi.org/) as `secret-scan-detector`.

## 2. Research & Strategy
*   **Packaging**: Use `pyproject.toml` with a build backend (e.g., `setuptools` or `hatchling`).
*   **CD Pipeline**: Use the official `pypa/gh-action-pypi-publish` GitHub Action.
*   **Security**: Use Trusted Publishing (OIDC) between GitHub and PyPI to avoid long-lived API tokens.

## 3. Implementation Checklist
- [x] **Initial Setup**:
    - [x] Create `pyproject.toml` with metadata, dependencies, and `secret-scan` entry point.
    - [x] Create a `LICENSE` file (required for PyPI).
    - [ ] Manually register the project on PyPI (initial "dry-run" upload).
- [x] **Automated CD (GitHub Action)**:
    - [x] Create `.github/workflows/pypi-publish.yml`.
    - [x] Configure it to trigger on new tags (e.g., `v*`).
    - [ ] Set up Trusted Publishing on PyPI for the `JMartynov/secret-scan` repository.
    - [x] Add build steps (generate `.tar.gz` and `.whl`).
    - [x] Add the publish step to upload artifacts to PyPI.

## 4. Testing & Verification
- [ ] **TestPyPI**: Perform a trial run to the TestPyPI environment to verify the packaging and upload logic.
- [x] **Installation**: Run `pip install secret-scan-detector` in a clean environment and verify functionality.

## 5. Engineering Standards
*   **SemVer**: Strictly follow Semantic Versioning.
*   **Immutability**: Once a version is published, it cannot be overwritten.
*   **Provenance**: Use GitHub's build provenance features to sign artifacts.
