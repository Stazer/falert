from asyncio import create_task
from json import loads
from uuid import UUID

from sanic.views import HTTPMethodView
from sanic.request import Request
from sanic.response import text, HTTPResponse, empty

from falert.backend.common.input import SubscriptionInputSchema
from falert.backend.common.output import (
    TriggerMatchingOutput,
    TriggerMatchingOutputSchema,
)
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
            subscription_entity.subscription_vertices.append(
                SubscriptionVertexEntity(
                    longitude=vertex.longitude,
                    latitude=vertex.latitude,
                )
            )

        subscription_entity.phone_number = subscription_input.phone_number

        request.ctx.database_session.add(subscription_entity)
        await request.ctx.database_session.commit()

        trigger_matching_output = TriggerMatchingOutput(
            subscription_ids=[
                UUID(
                    str(subscription_entity.id)
                ),  # properly satisfy the type checker here
            ],
        )

        create_task(
            request.ctx.sender.send(
                "trigger_matching",
                TriggerMatchingOutputSchema().dumps(
                    trigger_matching_output,
                ),
            )
        )

        return empty(status=201)
