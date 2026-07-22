from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = UserRepository(session)

    async def create_user(self, data: UserCreate) -> UserResponse:
        user = await self.repository.create(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
        )
        return UserResponse.model_validate(user)

    async def get_user(self, user_id: int) -> UserResponse | None:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            return None
        return UserResponse.model_validate(user)

    async def get_all_users(self) -> list[UserResponse]:
        users = await self.repository.get_all()
        return [UserResponse.model_validate(u) for u in users]

    async def update_user(self, user_id: int, data: UserUpdate) -> UserResponse | None:
        user = await self.repository.update(
            user_id=user_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
        )
        if user is None:
            return None
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)
