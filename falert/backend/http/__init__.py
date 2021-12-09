from sanic import Sanic

from falert.backend.common.application import BaseApplication
from falert.backend.http.view import PingView


class Application(BaseApplication):
    @staticmethod
    def run():
        Application().main()

    def __init__(self):
        super().__init__()

        self.__sanic = Sanic(
            name="falert.backend.http",
        )

        self.__sanic.add_route(PingView.as_view(), "/ping")

    def main(self):
        self.__sanic.run()
