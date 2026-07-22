"""Tests for users CRUD endpoints."""

import pytest
import pytest_asyncio
from httpx import ASGITransport
from httpx import AsyncClient

from app.db.models import metadata
from app.main import app
from app.core.config import DATABASE_TEST_URL
from app.routers.users import get_db_session
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker


@pytest_asyncio.fixture
def test_engine() -> AsyncEngine:
    """Create a test database engine."""
    engine = create_async_engine(DATABASE_TEST_URL, echo=False)
    return engine


@pytest_asyncio.fixture
async def setup_test_db(test_engine: AsyncEngine) -> AsyncEngine:
    """Create tables in test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client(setup_test_db: AsyncEngine) -> AsyncClient:
    """Create a test client with overridden dependencies."""
    session_factory = async_sessionmaker(setup_test_db, expire_on_commit=False)

    async def override_get_db_session() -> AsyncSession:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient) -> None:
    """Test creating a new user."""
    response = await client.post(
        "/api/v1/users",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_user_invalid_email(client: AsyncClient) -> None:
    """Test creating a user with invalid email."""
    response = await client.post(
        "/api/v1/users",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_missing_fields(client: AsyncClient) -> None:
    """Test creating a user with missing required fields."""
    response = await client.post(
        "/api/v1/users",
        json={"first_name": "John"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient) -> None:
    """Test getting a user by ID."""
    # Create a user first
    create_response = await client.post(
        "/api/v1/users",
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
        },
    )
    user_id = create_response.json()["id"]

    # Get the user
    response = await client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == "jane.smith@example.com"


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient) -> None:
    """Test getting a non-existent user."""
    response = await client.get("/api/v1/users/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_all_users(client: AsyncClient) -> None:
    """Test getting all users."""
    # Create multiple users
    for name in [("Alice", "Wonder"), ("Bob", "Builder")]:
        await client.post(
            "/api/v1/users",
            json={
                "first_name": name[0],
                "last_name": name[1],
                "email": f"{name[0].lower()}@example.com",
            },
        )

    response = await client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient) -> None:
    """Test updating a user."""
    # Create a user
    create_response = await client.post(
        "/api/v1/users",
        json={
            "first_name": "Original",
            "last_name": "Name",
            "email": "original@example.com",
        },
    )
    user_id = create_response.json()["id"]

    # Update the user
    response = await client.put(
        f"/api/v1/users/{user_id}",
        json={"first_name": "Updated", "last_name": "Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"
    assert data["last_name"] == "Name"
    assert data["email"] == "original@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found(client: AsyncClient) -> None:
    """Test updating a non-existent user."""
    response = await client.put(
        "/api/v1/users/99999",
        json={"first_name": "Nobody"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient) -> None:
    """Test deleting a user."""
    # Create a user
    create_response = await client.post(
        "/api/v1/users",
        json={
            "first_name": "ToDelete",
            "last_name": "User",
            "email": "delete@example.com",
        },
    )
    user_id = create_response.json()["id"]

    # Delete the user
    response = await client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204

    # Verify user is deleted
    get_response = await client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found(client: AsyncClient) -> None:
    """Test deleting a non-existent user."""
    response = await client.delete("/api/v1/users/99999")
    assert response.status_code == 404
