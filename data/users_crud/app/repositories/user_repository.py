from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import users


@dataclass
class UserRow:
    id: int
    first_name: str
    last_name: str
    email: str

    @classmethod
    def from_row(cls, row: dict) -> "UserRow":
        return cls(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
        )


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self, first_name: str, last_name: str, email: str
    ) -> UserRow:
        insert_stmt = users.insert().values(
            first_name=first_name, last_name=last_name, email=email
        )
        result = await self.session.execute(insert_stmt)
        user_id = result.inserted_primary_key[0]
        await self.session.commit()
        return UserRow(id=user_id, first_name=first_name, last_name=last_name, email=email)

    async def get_by_id(self, user_id: int) -> UserRow | None:
        stmt = select(users).where(users.c.id == user_id)
        result = await self.session.execute(stmt)
        row = result.fetchone()
        if row is None:
            return None
        return UserRow.from_row(row._asdict())

    async def get_all(self) -> list[UserRow]:
        stmt = select(users)
        result = await self.session.execute(stmt)
        rows = result.fetchall()
        return [UserRow.from_row(row._asdict()) for row in rows]

    async def update(
        self, user_id: int, first_name: str, last_name: str, email: str
    ) -> UserRow | None:
        update_stmt = (
            users.update()
            .where(users.c.id == user_id)
            .values(first_name=first_name, last_name=last_name, email=email)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        if result.rowcount == 0:
            return None
        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        delete_stmt = users.delete().where(users.c.id == user_id)
        result = await self.session.execute(delete_stmt)
        await self.session.commit()
        return result.rowcount > 0
