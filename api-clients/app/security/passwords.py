"""Password hashing utilities."""

from passlib.context import CryptContext

# Configure bcrypt  
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__default_rounds=12,
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit. We manually truncate to first 72 bytes.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The bcrypt hash
    """
    # Manually truncate to 72 bytes if password is longer
    # This is safe because bcrypt only uses first 72 bytes anyway
    if len(password.encode('utf-8')) > 72:
        # Simple byte truncation - bcrypt will handle it
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hash to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    # Manually truncate to 72 bytes if password is longer
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    return pwd_context.verify(plain_password, hashed_password)
