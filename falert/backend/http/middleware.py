from sanic.request import Request
from sanic.response import HTTPResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker


class BaseMiddleware:
    pass


class AttachDatabaseMiddleware(BaseMiddleware):
    def __init__(self, engine: AsyncEngine):
        self.__engine = engine

    async def __call__(self, request: Request):
        session_maker = sessionmaker(
            self.__engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with session_maker() as session:
            request.ctx.database_session = session


class DetachDatabaseMiddleware(BaseMiddleware):
    async def __call__(self, request: Request, _response: HTTPResponse):
        if hasattr(request.ctx, "database_session"):
            await request.ctx.database_session.close()
