from sanic import Sanic
from sanic.response import HTTPResponse
from sqlalchemy.ext.asyncio import create_async_engine

from falert.backend.common.application import BaseApplication
from falert.backend.http.view import PingView, SubscriptionCreateView
from falert.backend.http.middleware import (
    AttachDatabaseMiddleware,
    DetachDatabaseMiddleware,
)
from falert.backend.common.entity import BaseEntity


class Application(BaseApplication):
    @staticmethod
    def run():
        Application().main()

    async def __before_server_start(self, *_args, **_kwargs):
        async with self.__engine.begin() as connection:
            await connection.run_sync(BaseEntity.metadata.create_all)

    def __register_listeners(self):
        self.__sanic.register_listener(
            self.__before_server_start,
            "before_server_start",
        )

    def __register_middlewares(self):
        self.__sanic.register_middleware(
            AttachDatabaseMiddleware(self.__engine),
            "request",
        )

        self.__sanic.register_middleware(
            DetachDatabaseMiddleware(),
            "response",
        )

    def __register_routes(self):
        self.__sanic.add_route(PingView.as_view(), "/ping")
        self.__sanic.add_route(SubscriptionCreateView.as_view(), "/subscriptions")

    def __init__(self):
        super().__init__()

        self.__engine = create_async_engine(
            "sqlite+aiosqlite:///database.db",
            echo=True,
        )

        self.__sanic = Sanic(
            name="falert-backend-http",
        )

        self.__register_listeners()
        self.__register_middlewares()
        self.__register_routes()

    def main(self):
        self.__sanic.run()
