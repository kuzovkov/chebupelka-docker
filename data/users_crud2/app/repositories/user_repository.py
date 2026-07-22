"""User repository — data access layer."""

from collections.abc import Sequence
from typing import Any

from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import users


class UserRepository:
    """Repository for user CRUD operations using SQLAlchemy Core."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, first_name: str, last_name: str, email: str) -> dict[str, Any]:
        """Create a new user and return the created record."""
        stmt = insert(users).values(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        result = await self.session.execute(stmt)
        user_id = result.inserted_primary_key[0]
        await self.session.commit()
        return {
            "id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }

    async def get_by_id(self, user_id: int) -> dict[str, Any] | None:
        """Get a user by ID."""
        stmt = select(users).where(users.c.id == user_id)
        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            return None
        return dict(row._mapping)

    async def get_all(self) -> Sequence[dict[str, Any]]:
        """Get all users."""
        stmt = select(users)
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]

    async def update(
        self,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any] | None:
        """Update a user by ID. Returns updated user or None if not found."""
        # Check existence
        existing = await self.get_by_id(user_id)
        if existing is None:
            return None

        values: dict[str, str] = {}
        if first_name is not None:
            values["first_name"] = first_name
        if last_name is not None:
            values["last_name"] = last_name
        if email is not None:
            values["email"] = email

        stmt = update(users).where(users.c.id == user_id).values(**values)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        """Delete a user by ID. Returns True if deleted, False if not found."""
        existing = await self.get_by_id(user_id)
        if existing is None:
            return False
        stmt = delete(users).where(users.c.id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return True
