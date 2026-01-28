"""Password hashing utilities.

Prefer using the `bcrypt` package directly (avoids passlib backend detection issues
in some test environments). Always truncate to 72 bytes before calling bcrypt
since bcrypt only uses the first 72 bytes of the password.
"""

from datetime import datetime
from typing import Optional

try:
    import bcrypt  # type: ignore
except Exception:  # pragma: no cover - bcrypt should be available in runtime
    bcrypt = None  # type: ignore


DEFAULT_ROUNDS = 12


def _truncate_to_72(s: str) -> bytes:
    b = s.encode("utf-8")
    if len(b) > 72:
        return b[:72]
    return b


def hash_password(password: str, rounds: int = DEFAULT_ROUNDS) -> str:
    """Hash a password using bcrypt.

    Args:
        password: plain text password
        rounds: bcrypt rounds (cost)

    Returns:
        str: hashed password (utf-8)
    """
    pw = _truncate_to_72(password)
    if bcrypt is not None:
        salt = bcrypt.gensalt(rounds=rounds)
        hashed = bcrypt.hashpw(pw, salt)
        return hashed.decode("utf-8")

    # Fallback to passlib if bcrypt package is not available
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # passlib expects str input
    return pwd_context.hash(pw.decode("utf-8", errors="ignore"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.

    Args:
        plain_password: plain text password
        hashed_password: stored bcrypt hash

    Returns:
        bool
    """
    pw = _truncate_to_72(plain_password)
    if bcrypt is not None:
        try:
            return bcrypt.checkpw(pw, hashed_password.encode("utf-8"))
        except Exception:
            # If checkpw fails for any reason, fall through to passlib
            pass

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(pw.decode("utf-8", errors="ignore"), hashed_password)

