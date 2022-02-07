from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine() -> AsyncEngine:
    return create_async_engine(
        "sqlite+aiosqlite:///database.db",
        echo=True,
    )
