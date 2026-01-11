"""Password hashing utilities."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password.
    
    Truncates password to 72 bytes (bcrypt's limit) to avoid errors.
    This is safe as bcrypt only uses the first 72 bytes anyway.
    """
    # Truncate to 72 bytes to avoid bcrypt error
    # This is safe as bcrypt only uses first 72 bytes
    password_bytes = password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password_truncated)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Truncates password to 72 bytes to match hashing behavior.
    """
    # Truncate to 72 bytes to match hash_password behavior
    password_bytes = plain_password.encode('utf-8')[:72]
    password_truncated = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(password_truncated, hashed_password)
