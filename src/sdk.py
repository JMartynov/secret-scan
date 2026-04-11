import asyncio
from typing import List, Literal, Any
from functools import wraps
from contextlib import contextmanager

from src.detector import SecretDetector
from src.obfuscator import Obfuscator

class SecurityException(Exception):
    """Exception raised when a security violation is detected."""
    pass

class Scanner:
    """
    Developer-friendly SDK for integrating secret scanning into applications.
    """
    def __init__(
        self,
        obfuscate: bool = False,
        obfuscate_mode: Literal["redact", "hash", "synthetic"] = "redact",
        min_risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW",
        data_dir: str = 'data'
    ):
        self.engine = SecretDetector(data_dir=data_dir)
        self.obfuscate = obfuscate
        self.obfuscator = Obfuscator(mode=obfuscate_mode) if obfuscate else None
        self.min_risk_level = min_risk_level
        self._risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    def _meets_risk_threshold(self, risk: str) -> bool:
        return self._risk_levels.get(risk.upper(), 0) >= self._risk_levels.get(self.min_risk_level.upper(), 0)

    def scan(self, text: str) -> List[Any]:
        """
        Scans a string for secrets.
        """
        results = self.engine.engine.detect(text)
        # findings from engine.detect are `Finding` objects, so we need to access attributes
        return [r for r in results if hasattr(r, 'risk') and self._meets_risk_threshold(r.risk)]

    def redact(self, text: str) -> str:
        """
        Scans and redacts a string based on initialization settings.
        """
        if not self.obfuscate or not self.obfuscator:
            return text
        results = self.scan(text)
        if not results:
            return text
        return self.obfuscator.obfuscate(text, results)

    def validate(self, text: str) -> str:
        """
        Scans a string and raises SecurityException if a secret is found.
        Otherwise returns the string.
        """
        results = self.scan(text)
        if results:
            raise SecurityException(f"Security violation: Secret detected in input (risk: {getattr(results[0], 'risk', 'LOW')})")
        return text

    @contextmanager
    def session(self, mode: Literal["block", "log"] = "block"):
        """
        Context manager for processing batches of items.
        """
        class SessionWrapper:
            def __init__(self, scanner: Scanner, mode: str):
                self.scanner = scanner
                self.mode = mode

            def validate(self, text: str) -> str:
                results = self.scanner.scan(text)
                if results:
                    msg = f"Security violation: Secret detected (risk: {getattr(results[0], 'risk', 'LOW')})"
                    if self.mode == "block":
                        raise SecurityException(msg)
                    else:
                        print(f"WARN: {msg}") # In a real app this would use logging
                return text

            def redact(self, text: str) -> str:
                return self.scanner.redact(text)

        yield SessionWrapper(self, mode)

class AsyncScanner(Scanner):
    """
    Asynchronous version of the Scanner SDK.
    """
    async def scan(self, text: str) -> List[Any]:
        # Since the core engine is synchronous, we run it in a thread pool
        # to avoid blocking the event loop for large strings
        return await asyncio.to_thread(super().scan, text)

    async def redact(self, text: str) -> str:
        if not self.obfuscate or not self.obfuscator:
            return text
        results = await self.scan(text)
        if not results:
            return text
        return self.obfuscator.obfuscate(text, results)

    async def validate(self, text: str) -> str:
        results = await self.scan(text)
        if results:
            raise SecurityException(f"Security violation: Secret detected in input (risk: {getattr(results[0], 'risk', 'LOW')})")
        return text

def secure_prompt(obfuscate: bool = True, obfuscate_mode: Literal["redact", "hash", "synthetic"] = "redact", min_risk_level="LOW"):
    """
    Decorator to automatically scan/redact string arguments to a function.
    """
    scanner = Scanner(obfuscate=obfuscate, obfuscate_mode=obfuscate_mode, min_risk_level=min_risk_level)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Redact string arguments
            new_args = []
            for arg in args:
                if isinstance(arg, str):
                    new_args.append(scanner.redact(arg))
                else:
                    new_args.append(arg)

            new_kwargs = {}
            for k, v in kwargs.items():
                if isinstance(v, str):
                    new_kwargs[k] = scanner.redact(v)
                else:
                    new_kwargs[k] = v

            return func(*new_args, **new_kwargs)
        return wrapper
    return decorator
