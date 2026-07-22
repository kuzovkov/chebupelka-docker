"""Application configuration."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'users_db.sqlite'}"
DATABASE_TEST_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'users_db_test.sqlite'}"
