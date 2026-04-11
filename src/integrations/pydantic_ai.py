from src.sdk import Scanner

def secret_validator(v: str) -> str:
    """A Pydantic validator that blocks secrets."""
    scanner = Scanner()
    scanner.validate(v)
    return v

def secret_redactor(v: str) -> str:
    """A Pydantic validator that redacts secrets."""
    scanner = Scanner(obfuscate=True)
    return scanner.redact(v)
