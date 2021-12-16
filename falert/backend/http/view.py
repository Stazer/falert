from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.response import text, HTTPResponse


class BaseView(HTTPMethodView):
    pass


class PingView(BaseView):
    @staticmethod
    def get(_request: Request) -> HTTPResponse:
        return text("pong")
