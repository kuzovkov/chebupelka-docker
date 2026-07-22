"""Users REST router."""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.models import get_async_engine
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.schemas.user import UserResponse
from app.schemas.user import UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

_engine = None
_session_factory = None


async def get_engine():
    """Get or create async engine."""
    global _engine
    if _engine is None:
        _engine = get_async_engine()
    return _engine


async def get_session_factory():
    """Get or create session factory."""
    global _session_factory
    if _session_factory is None:
        engine = await get_engine()
        _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _session_factory


async def get_db_session() -> AsyncSession:
    """Dependency: yield a database session."""
    factory = await get_session_factory()
    async with factory() as session:
        yield session


async def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """Dependency: yield a user repository."""
    return UserRepository(session)


async def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    """Dependency: yield a user service."""
    return UserService(repository)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user."""
    result = await service.create_user(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
    )
    return UserResponse(**result)


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Get all users",
)
async def get_users(
    service: UserService = Depends(get_user_service),
) -> list[UserResponse]:
    """Get all users."""
    results = await service.get_all_users()
    return [UserResponse(**u) for u in results]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID",
)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get a user by ID."""
    result = await service.get_user(user_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return UserResponse(**result)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user",
)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Update a user."""
    result = await service.update_user(
        user_id=user_id,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return UserResponse(**result)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
async def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> None:
    """Delete a user."""
    deleted = await service.delete_user(user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return None
