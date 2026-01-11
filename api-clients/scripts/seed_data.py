"""Seed database with test data."""
import asyncio
import os
import sys
import uuid

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime

from app.database import AsyncSessionLocal
from app.models.address import Address, AddressType
from app.models.customer import Customer, CustomerStatus, CustomerType
from app.security.passwords import hash_password


async def seed_data():
    """Seed database with test data."""
    async with AsyncSessionLocal() as db:
        print("Seeding database with test data...")

        # Create admin user
        admin = Customer(
            id=uuid.uuid4(),
            reference="CLI20240101ADMIN",
            civilite="M",
            nom="Admin",
            prenom="Super",
            email="admin@payetonkawa.fr",
            telephone="0123456789",
            type_client=CustomerType.ADMIN,
            statut=CustomerStatus.ACTIF,
            hashed_password=hash_password("admin123"[:72]),
            email_confirme=True,
        )
        db.add(admin)

        # Create test customer
        customer = Customer(
            id=uuid.uuid4(),
            reference="CLI20240101TEST1",
            civilite="Mme",
            nom="Dupont",
            prenom="Marie",
            email="marie.dupont@example.com",
            telephone="0612345678",
            type_client=CustomerType.PARTICULIER,
            statut=CustomerStatus.ACTIF,
            hashed_password=hash_password("password123"[:72]),
            email_confirme=True,
        )
        db.add(customer)

        # Create address for test customer
        address = Address(
            id=uuid.uuid4(),
            client_id=customer.id,
            type_adresse=AddressType.LIVRAISON_FACTURATION,
            est_defaut=True,
            libelle="Domicile",
            destinataire="Marie Dupont",
            adresse_ligne1="123 Rue de la Paix",
            code_postal="75001",
            ville="Paris",
            pays="France",
        )
        db.add(address)

        # Create professional customer
        pro_customer = Customer(
            id=uuid.uuid4(),
            reference="CLI20240101PRO1",
            civilite="M",
            nom="Martin",
            prenom="Jean",
            email="contact@cafepro.fr",
            telephone="0145678901",
            type_client=CustomerType.PROFESSIONNEL,
            statut=CustomerStatus.ACTIF,
            raison_sociale="Café Pro SARL",
            siret="12345678901234",
            tva_intracommunautaire="FR12345678901",
            nom_contact="Jean Martin",
            hashed_password=hash_password("password123"[:72]),
            email_confirme=True,
        )
        db.add(pro_customer)

        await db.commit()
        print("Database seeded successfully!")
        print("\nTest accounts created:")
        print("- Admin: admin@payetonkawa.fr / admin123")
        print("- Customer: marie.dupont@example.com / password123")
        print("- Professional: contact@cafepro.fr / password123")


if __name__ == "__main__":
    asyncio.run(seed_data())
