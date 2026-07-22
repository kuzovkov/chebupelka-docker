from sqlalchemy import Column, Integer, MetaData, String, Table

metadata = MetaData()

users = Table(
    "users",
    metadata,
    # SQLite auto-increment only works with INTEGER type (which is 64-bit in SQLite).
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("first_name", String(200), nullable=False),
    Column("last_name", String(200), nullable=False),
    Column("email", String(255), nullable=False),
)
