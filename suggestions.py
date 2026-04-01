def get_suggestion(secret_type: str, category: str) -> str:
    """
    Returns an actionable suggestion based on the secret type or category.
    """
    category = category.lower()
    secret_type = secret_type.lower()

    if "aws" in secret_type or "amazon" in secret_type:
        return "Revoke this key immediately via AWS IAM and rotate to a new one. Consider using IAM Roles instead of hardcoded keys."
    if "github" in secret_type or "gitlab" in secret_type:
        return "Revoke this token in your VCS settings. Use fine-grained access tokens with minimal scopes."
    if "api" in secret_type or "key" in secret_type:
        return "Move this API key to an environment variable or secure secret manager (e.g., AWS Secrets Manager, HashiCorp Vault)."
    if "password" in secret_type or "credential" in secret_type:
        return "Do not hardcode passwords. Inject them at runtime via environment variables or a configuration server."
    if category == "entropy":
        return "If this is a real secret, store it securely. If it's a false positive, consider adding `# secretscan:ignore entropy` inline."

    return "Move this secret to a secure vault or environment variable and rotate it immediately if it was ever pushed."
