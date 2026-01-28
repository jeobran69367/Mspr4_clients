"""Repository for UserAuth model (refresh tokens / sessions)."""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_auth import UserAuth
from app.repositories.base_repository import BaseRepository


class UserAuthRepository(BaseRepository[UserAuth]):
    """Repository to manage UserAuth records."""

    def __init__(self, db: AsyncSession):
        super().__init__(UserAuth, db)

    async def get_by_token(self, token: str) -> Optional[UserAuth]:
        result = await self.db.execute(select(UserAuth).where(UserAuth.refresh_token == token))
        return result.scalar_one_or_none()

    async def list_by_customer(self, customer_id: str) -> List[UserAuth]:
        result = await self.db.execute(select(UserAuth).where(UserAuth.customer_id == customer_id))
        return list(result.scalars().all())

    async def delete_by_token(self, token: str) -> None:
        stmt = delete(UserAuth).where(UserAuth.refresh_token == token)
        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_by_customer(self, customer_id: str) -> None:
        stmt = delete(UserAuth).where(UserAuth.customer_id == customer_id)
        await self.db.execute(stmt)
        await self.db.commit()
