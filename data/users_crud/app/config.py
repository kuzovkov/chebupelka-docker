from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite+aiosqlite:///./users.db"
    test_database_url: str = "sqlite+aiosqlite:///./users_db_test.db"


settings = Settings()
