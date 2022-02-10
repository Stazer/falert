from json import loads

from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.response import text, HTTPResponse, empty

from falert.backend.common.input import SubscriptionInputSchema
from falert.backend.common.entity import SubscriptionEntity, SubscriptionVertexEntity


class BaseView(HTTPMethodView):
    pass


class PingView(BaseView):
    @staticmethod
    def get(_request: Request) -> HTTPResponse:
        return text("pong")


class SubscriptionCreateView(BaseView):
    @staticmethod
    async def post(request: Request) -> HTTPResponse:
        subscription_input = SubscriptionInputSchema().load(loads(request.body))
        subscription_entity = SubscriptionEntity()

        for vertex in subscription_input.vertices:
            subscription_entity.vertices.append(
                SubscriptionVertexEntity(
                    longitude=vertex.longitude,
                    latitude=vertex.latitude,
                )
            )

        request.ctx.database_session.add(subscription_entity)

        await request.ctx.database_session.commit()

        return empty(status=201)
