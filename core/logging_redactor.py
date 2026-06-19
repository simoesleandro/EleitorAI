"""Secret-redacting logging facility.

Intercepts ALL log records via `setLogRecordFactory` and scrubs:
- exact values from configured secrets (Gemini keys, Telegram tokens, etc.)
- generic `*_KEY=...`, `*_TOKEN=...`, `*_SECRET=...`, `*_HASH=...`, `*_PASS=...` patterns

The factory approach ensures coverage of every log record in the process,
regardless of which logger is used.
"""
import logging
import re
from typing import Iterable, Optional

REDACTED = "***REDACTED***"

_KEY_VALUE_PATTERN = re.compile(
    r"((?:GEMINI|TELEGRAM|LANGFUSE|ADMIN|SECRET|API|TOKEN|PASSWORD|PASS|HASH)_?[A-Z_]*?(?:KEY|TOKEN|SECRET|HASH|PASSWORD|PASS|ID)?)"
    r"(\s*[=:]\s*)"
    r"(\"[^\"]*\"|(?<![%])\b[^\s,;}\)\]]+)",
    re.IGNORECASE,
)


class SecretRedactingFilter(logging.Filter):
    """Redacts secrets from log records. Useful when attached to specific handlers.

    For whole-process coverage, prefer `install_redactor()` which uses
    `setLogRecordFactory` and intercepts every LogRecord at creation time.
    """

    def __init__(self, secrets: Optional[Iterable[str]] = None, min_length: int = 8):
        super().__init__()
        self._min_length = min_length
        self._secrets: list[str] = [s for s in (secrets or []) if s and len(s) >= min_length]

    def update_secrets(self, secrets: Iterable[str]) -> None:
        self._secrets = [s for s in secrets if s and len(s) >= self._min_length]

    def redact(self, text: str) -> str:
        if not text:
            return text
        for secret in self._secrets:
            if secret in text:
                text = text.replace(secret, REDACTED)
        text = _KEY_VALUE_PATTERN.sub(
            lambda m: f"{m.group(1)}{m.group(2)}{REDACTED}" if m.group(3).startswith('"')
            else f'{m.group(1)}{m.group(2)}"{REDACTED}"',
            text,
        )
        return text

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if isinstance(record.msg, str):
                record.msg = self.redact(record.msg)
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {k: self.redact(str(v)) if isinstance(v, str) else v
                                   for k, v in record.args.items()}
                else:
                    record.args = tuple(
                        self.redact(a) if isinstance(a, str) else a for a in record.args
                    )
        except Exception:
            pass
        return True


_OLD_FACTORY = None
_ACTIVE_REDACTOR: Optional[SecretRedactingFilter] = None


def _collect_secrets() -> list[str]:
    """Pull current secret values from settings."""
    from core.config import get_settings
    s = get_settings()
    candidates = [
        s.gemini_api_key,
        s.telegram_bot_token,
        s.telegram_api_hash,
        s.admin_pass,
        s.secret_key,
        s.langfuse_public_key,
        s.langfuse_secret_key,
        getattr(s, "portal_transparencia_api_key", None),
    ]
    return [c for c in candidates if c]


def _redacting_factory(old_factory, redactor: SecretRedactingFilter):
    """Wrap an existing LogRecord factory to apply the redactor."""
    def factory(*args, **kwargs):
        record = old_factory(*args, **kwargs) if old_factory else logging.LogRecord(*args, **kwargs)
        redactor.filter(record)
        return record
    return factory


def install_redactor() -> SecretRedactingFilter:
    """Install a process-wide log record factory that redacts secrets.

    Idempotent. Re-running refreshes the secret list from current settings.
    """
    global _OLD_FACTORY, _ACTIVE_REDACTOR
    redactor = SecretRedactingFilter(secrets=_collect_secrets())
    if _ACTIVE_REDACTOR is not None:
        _ACTIVE_REDACTOR.update_secrets(redactor._secrets)
        return _ACTIVE_REDACTOR
    _OLD_FACTORY = logging.getLogRecordFactory()
    logging.setLogRecordFactory(_redacting_factory(_OLD_FACTORY, redactor))
    _ACTIVE_REDACTOR = redactor
    return redactor


def uninstall_redactor() -> None:
    """Restore the previous log record factory. Mostly for tests."""
    global _OLD_FACTORY, _ACTIVE_REDACTOR
    if _OLD_FACTORY is not None:
        logging.setLogRecordFactory(_OLD_FACTORY)
    _OLD_FACTORY = None
    _ACTIVE_REDACTOR = None
