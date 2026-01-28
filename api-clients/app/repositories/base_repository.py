"""Base repository pattern."""

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """Initialize repository."""
        self.model = model
        self.db = db

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get a record by ID."""
        # Check if model has relationships to eagerly load
        stmt = select(self.model).where(self.model.id == id)
        # For Customer model, eagerly load addresses
        if hasattr(self.model, 'adresses'):
            stmt = stmt.options(selectinload(self.model.adresses))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update a record."""
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a record."""
        await self.db.delete(obj)
        await self.db.commit()

    async def count(self) -> int:
        """Count total records."""
        from sqlalchemy import func

        result = await self.db.execute(select(func.count()).select_from(self.model))
        return result.scalar_one()
