import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import metadata, users

TEST_DB_URL = "sqlite+aiosqlite:///./users_db_test.db"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


def override_get_session():
    async def _get_session():
        async with test_session_factory() as session:
            yield session

    return _get_session


app.dependency_overrides[get_session] = override_get_session()


@pytest_asyncio.fixture(autouse=True)
async def setup_and_teardown_db():
    """Create tables before each test and drop them after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.execute(text(f"DELETE FROM {users.name}"))
        await conn.commit()
    async with test_engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_create_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/users/",
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
    assert isinstance(data["id"], int)


@pytest.mark.asyncio
async def test_create_user_invalid_body() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/users/",
            json={"first_name": "John"},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            "/users/",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
            },
        )
        user_id = create_resp.json()["id"]

        get_resp = await client.get(f"/users/{user_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == "jane.smith@example.com"


@pytest.mark.asyncio
async def test_get_user_not_found() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/users/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_users() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            "/users/",
            json={
                "first_name": "Alice",
                "last_name": "Wonderland",
                "email": "alice@example.com",
            },
        )
        await client.post(
            "/users/",
            json={
                "first_name": "Bob",
                "last_name": "Builder",
                "email": "bob@example.com",
            },
        )

        list_resp = await client.get("/users/")
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_users_empty() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_update_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            "/users/",
            json={
                "first_name": "Original",
                "last_name": "Name",
                "email": "original@example.com",
            },
        )
        user_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/users/{user_id}",
            json={
                "first_name": "Updated",
                "last_name": "Name",
                "email": "updated@example.com",
            },
        )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["first_name"] == "Updated"
    assert data["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.put(
            "/users/99999",
            json={
                "first_name": "Nobody",
                "last_name": "Here",
                "email": "nobody@example.com",
            },
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        create_resp = await client.post(
            "/users/",
            json={
                "first_name": "ToDelete",
                "last_name": "User",
                "email": "delete@example.com",
            },
        )
        user_id = create_resp.json()["id"]

        delete_resp = await client.delete(f"/users/{user_id}")
    assert delete_resp.status_code == 204

    # Verify user is gone
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        get_resp = await client.get(f"/users/{user_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_not_found() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete("/users/99999")
    assert response.status_code == 404
