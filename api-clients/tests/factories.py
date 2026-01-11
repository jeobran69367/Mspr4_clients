"""Test factories for creating test data."""

import uuid
from datetime import datetime

from app.models.address import Address, AddressType
from app.models.customer import Customer, CustomerStatus, CustomerType
from app.security.passwords import hash_password


def create_test_customer(**kwargs):
    """Create a test customer."""
    defaults = {
        "id": uuid.uuid4(),
        "reference": f"CLI{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}",
        "civilite": "M",
        "nom": "Dupont",
        "prenom": "Jean",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "telephone": "0123456789",
        "type_client": CustomerType.PARTICULIER,
        "statut": CustomerStatus.ACTIF,
        "hashed_password": hash_password("password123"),
        "email_confirme": True,
    }
    defaults.update(kwargs)
    return Customer(**defaults)


def create_test_address(customer_id: uuid.UUID, **kwargs):
    """Create a test address."""
    defaults = {
        "id": uuid.uuid4(),
        "client_id": customer_id,
        "type_adresse": AddressType.LIVRAISON_FACTURATION,
        "est_defaut": True,
        "libelle": "Domicile",
        "destinataire": "Test User",
        "adresse_ligne1": "123 Rue de Test",
        "code_postal": "75001",
        "ville": "Paris",
        "pays": "France",
    }
    defaults.update(kwargs)
    return Address(**defaults)
