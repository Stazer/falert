from sanic import Sanic
from sanic.response import HTTPResponse
from sqlalchemy.ext.asyncio import create_async_engine

from falert.backend.common.application import BaseApplication
from falert.backend.http.view import PingView
from falert.backend.http.middleware import (
    AttachDatabaseMiddleware,
    DetachDatabaseMiddleware,
)


class Application(BaseApplication):
    @staticmethod
    def run():
        Application().main()

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

    def __init__(self):
        super().__init__()

        self.__engine = create_async_engine(
            "sqlite+aiosqlite:///database.db",
            echo=True,
        )

        self.__sanic = Sanic(
            name="falert.backend.http",
        )

        self.__register_middlewares()
        self.__register_routes()

    def main(self):
        self.__sanic.run()
