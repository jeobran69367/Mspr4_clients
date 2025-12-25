"""Data formatters."""
from datetime import datetime
from typing import Optional


def format_phone_number(phone: str) -> str:
    """Format phone number to standard format."""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Format as XX XX XX XX XX
    if len(digits) == 10:
        return f"{digits[0:2]} {digits[2:4]} {digits[4:6]} {digits[6:8]} {digits[8:10]}"
    elif len(digits) == 11 and digits.startswith('33'):
        # +33 format
        return f"+33 {digits[2]} {digits[3:5]} {digits[5:7]} {digits[7:9]} {digits[9:11]}"
    
    return phone


def format_siret(siret: str) -> str:
    """Format SIRET number."""
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, siret))
    
    # Format as XXX XXX XXX XXXXX
    if len(digits) == 14:
        return f"{digits[0:3]} {digits[3:6]} {digits[6:9]} {digits[9:14]}"
    
    return siret


def format_date(date: Optional[datetime], format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[str]:
    """Format datetime to string."""
    if date is None:
        return None
    return date.strftime(format_str)


def format_customer_name(civilite: Optional[str], prenom: str, nom: str) -> str:
    """Format customer full name."""
    parts = []
    if civilite:
        parts.append(civilite)
    parts.append(prenom)
    parts.append(nom)
    return " ".join(parts)
