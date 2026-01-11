"""Password hashing utilities."""

from passlib.context import CryptContext

# Configure bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto"
)


def hash_password(password: str) -> str:
    """Hash a password.
    
    Bcrypt has a 72-byte limit, so we truncate manually to avoid ValueError.
    This is safe because bcrypt only uses the first 72 bytes anyway.
    """
    # Convert to bytes and truncate to 72 bytes (bcrypt's hard limit)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Convert back to string for passlib
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Bcrypt has a 72-byte limit, so we truncate manually to avoid ValueError.
    """
    # Convert to bytes and truncate to 72 bytes (bcrypt's hard limit)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    # Convert back to string for passlib
    truncated_password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)
