"""Create a UserAuth (refresh token) record for a customer.

Usage (from project root api-clients):
  python scripts/create_user_auth.py --email admin@payetonkawa.fr

Options:
  --email EMAIL       Lookup customer by email
  --customer-id ID    Use customer id directly
  --token TOKEN       Provide explicit refresh token (optional)
  --days N            Token expiry in days (default from settings)

This script uses the project's AsyncSessionLocal and settings.
"""
import argparse
import asyncio
import uuid
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from app.database import AsyncSessionLocal
from app.models.user_auth import UserAuth
from app.models.customer import Customer
from app.security.auth import create_refresh_token
from app.config import settings


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", help="customer email to lookup")
    parser.add_argument("--customer-id", help="customer id (uuid)")
    parser.add_argument("--token", help="explicit refresh token to store")
    parser.add_argument("--days", type=int, help="expiry in days")
    args = parser.parse_args()

    if not args.email and not args.customer_id:
        print("Provide either --email or --customer-id")
        return

    async with AsyncSessionLocal() as db:
        # find customer
        if args.email:
            result = await db.execute(Customer.__table__.select().where(Customer.email == args.email))
            row = result.first()
            if not row:
                print(f"Customer not found with email {args.email}")
                return
            customer = Customer(**row._mapping)
            customer_id = customer.id
        else:
            customer_id = args.customer_id

        token = args.token or create_refresh_token({"sub": str(customer_id)})
        days = args.days or settings.REFRESH_TOKEN_EXPIRE_DAYS
        expiry = datetime.utcnow() + timedelta(days=days)

        ua = UserAuth(
            id=uuid.uuid4(),
            customer_id=customer_id,
            refresh_token=token,
            token_expiry=expiry,
            device_info="script-created",
        )
        db.add(ua)
        await db.commit()
        print("UserAuth created:")
        print(" id:", ua.id)
        print(" customer_id:", ua.customer_id)
        print(" refresh_token:", ua.refresh_token)
        print(" token_expiry:", ua.token_expiry)


if __name__ == "__main__":
    asyncio.run(main())
