from sanic import Sanic
from sanic.response import HTTPResponse
from sanic_ext import Extend

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
        async with self._engine.begin() as connection:
            await connection.run_sync(BaseEntity.metadata.create_all)

    def __init__(self) -> None:
        super().__init__()

        self.__sanic = Sanic(
            name="falert-backend-http",
        )

        self.__sanic.config.CORS_ORIGINS = "*"
        self.__sanic.config.CORS_SEND_WILDCARD = True
        Extend(self.__sanic)

        self.__sanic.register_middleware(
            AttachDatabaseMiddleware(self._engine),
            "request",
        )

        self.__sanic.register_middleware(
            DetachDatabaseMiddleware(),
            "response",
        )

        self.__sanic.register_listener(
            self.__before_server_start,
            "before_server_start",
        )

        self.__sanic.add_route(PingView.as_view(), "/ping")
        self.__sanic.add_route(SubscriptionCreateView.as_view(), "/subscriptions")

    def main(self):
        self.__sanic.run()
