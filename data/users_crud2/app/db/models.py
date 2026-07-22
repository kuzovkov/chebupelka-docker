"""SQLAlchemy Core table definitions."""

from sqlalchemy import Column
from sqlalchemy import create_engine
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import DATABASE_URL

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String(200), nullable=False),
    Column("last_name", String(200), nullable=False),
    Column("email", String(255), nullable=False),
)


def get_async_engine() -> AsyncEngine:
    """Create and return an async SQLAlchemy engine."""
    return create_async_engine(DATABASE_URL, echo=False)


def get_sync_engine() -> Engine:
    """Create and return a sync SQLAlchemy engine for migrations."""
    sync_url = DATABASE_URL.replace("+aiosqlite", "")
    return create_engine(sync_url, echo=False)
