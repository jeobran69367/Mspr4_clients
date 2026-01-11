"""Password hashing utilities."""

from passlib.context import CryptContext

# Configure bcrypt to allow truncation (truncate_error=False)
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__truncate_error=False
)


def hash_password(password: str) -> str:
    """Hash a password.
    
    Bcrypt is configured to automatically truncate passwords > 72 bytes.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.
    
    Bcrypt automatically truncates passwords > 72 bytes for verification.
    """
    return pwd_context.verify(plain_password, hashed_password)
