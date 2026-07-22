"""User service — business logic layer."""

from collections.abc import Sequence
from typing import Any

from app.repositories.user_repository import UserRepository


class UserService:
    """Service for user operations."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def create_user(
        self, first_name: str, last_name: str, email: str
    ) -> dict[str, Any]:
        """Create a new user."""
        return await self.repository.create(first_name, last_name, email)

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        """Get a user by ID."""
        return await self.repository.get_by_id(user_id)

    async def get_all_users(self) -> Sequence[dict[str, Any]]:
        """Get all users."""
        return await self.repository.get_all()

    async def update_user(
        self,
        user_id: int,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any] | None:
        """Update a user."""
        return await self.repository.update(user_id, first_name, last_name, email)

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return await self.repository.delete(user_id)
