"""Password hashing utilities."""

from passlib.context import CryptContext

# Configure bcrypt with truncate_error disabled to allow automatic truncation
# This prevents ValueError when passwords exceed 72 bytes
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__ident="2b",
    bcrypt__default_rounds=12,
)


def _truncate_password(password: str) -> str:
    """Safely truncate password to 72 bytes for bcrypt.
    
    Bcrypt has a hard 72-byte limit. This function truncates the password
    to fit within that limit while preserving UTF-8 character boundaries.
    
    Args:
        password: The password string to truncate
        
    Returns:
        str: Password truncated to at most 72 bytes when encoded as UTF-8
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password
    
    # Truncate to 72 bytes, being careful not to split multi-byte UTF-8 characters
    truncated = password_bytes[:72]
    
    # Try to decode - if it fails, keep removing bytes until it works
    # This ensures we don't break in the middle of a multi-byte character
    while len(truncated) > 0:
        try:
            return truncated.decode('utf-8')
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    
    # Fallback (should never happen with valid UTF-8 input)
    return ''


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.
    
    Bcrypt has a 72-byte limit. We truncate passwords to 72 bytes
    while preserving UTF-8 character boundaries before hashing.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The bcrypt hash
    """
    truncated_password = _truncate_password(password)
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The bcrypt hash to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    truncated_password = _truncate_password(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)
