"""Data validators."""
import re


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate French phone number."""
    # French phone numbers: 0X XX XX XX XX or +33 X XX XX XX XX
    pattern = r'^(?:(?:\+|00)33|0)[1-9](?:[0-9]{2}){4}$'
    cleaned = phone.replace(' ', '').replace('.', '').replace('-', '')
    return bool(re.match(pattern, cleaned))


def validate_siret(siret: str) -> bool:
    """Validate French SIRET number (14 digits)."""
    if not siret or len(siret) != 14 or not siret.isdigit():
        return False

    # Luhn algorithm for SIRET validation
    total = 0
    for i, digit in enumerate(siret):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    return total % 10 == 0


def validate_postal_code(postal_code: str, country: str = "France") -> bool:
    """Validate postal code based on country."""
    if country == "France":
        # French postal codes: 5 digits
        return bool(re.match(r'^\d{5}$', postal_code))
    return True  # Accept any format for other countries


def validate_tva_intracommunautaire(tva: str) -> bool:
    """Validate French VAT number."""
    # French VAT: FR + 2 characters + 9 digits
    pattern = r'^FR[A-Z0-9]{2}\d{9}$'
    return bool(re.match(pattern, tva.upper()))
