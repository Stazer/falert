from uuid import UUID
from typing import List, Optional, Tuple
from datetime import timedelta, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy import select
from shapely.geometry import Point, Polygon

from falert.backend.common.input import TriggerMatchingInputSchema
from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.messenger import AsyncpgReceiver
from falert.backend.common.entity import (
    SubscriptionEntity,
    SubscriptionMatchEntity,
    SubscriptionMatchFireLocationEntity,
    FireLocationEntity,
)


class Application(AsynchronousApplication):
    def __init__(self):
        super().__init__()

        # pylint: disable=unused-private-member
        self.__receiver = None

    async def main(self):
        async with self._engine.begin() as connection:
            raw_connection = await connection.get_raw_connection()

            # pylint: disable=unused-private-member
            self.__receiver = AsyncpgReceiver(
                raw_connection.dbapi_connection.driver_connection
            )

            await self.__handle_matching(None, None)

            while True:
                trigger_matching_input = TriggerMatchingInputSchema().loads(
                    await self.__receiver.receive("trigger_matching")
                )

                await self.__handle_matching(
                    trigger_matching_input.subscription_ids,
                    trigger_matching_input.dataset_harvest_ids,
                )

    async def __handle_matching(
        self,
        subscription_ids: Optional[List[UUID]],
        dataset_harvest_ids: Optional[List[UUID]],
    ) -> None:
        session_maker = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        fire_location_entities = []
        subscription_entities = []

        async with session_maker() as database_session:
            if dataset_harvest_ids is None or len(dataset_harvest_ids) == 0:
                fire_location_entities = list(
                    await database_session.execute(
                        select(FireLocationEntity).where(
                            FireLocationEntity.created
                            >= datetime.utcnow() - timedelta(hours=24)
                        )
                    )
                )
            else:
                fire_location_entities = list(
                    await database_session.execute(
                        select(FireLocationEntity).where(
                            FireLocationEntity.dataset_harvest_id.in_(
                                dataset_harvest_ids
                            )
                        )
                    )
                )

            if subscription_ids is None or len(subscription_ids) == 0:
                subscription_entities = list(
                    (
                        await database_session.execute(
                            select(SubscriptionEntity)
                            .options(
                                joinedload(SubscriptionEntity.subscription_vertices)
                            )
                            .options(
                                joinedload(
                                    SubscriptionEntity.subscription_matches
                                ).joinedload(
                                    SubscriptionMatchEntity.subscription_match_fire_locations
                                )
                            )
                        )
                    ).unique()
                )
            else:
                subscription_entities = list(
                    (
                        await database_session.execute(
                            select(SubscriptionEntity)
                            .where(SubscriptionEntity.id.in_(subscription_ids))
                            .options(
                                joinedload(SubscriptionEntity.subscription_vertices)
                            )
                            .options(
                                joinedload(
                                    SubscriptionEntity.subscription_matches
                                ).joinedload(
                                    SubscriptionMatchEntity.subscription_match_fire_locations
                                )
                            )
                        )
                    ).unique()
                )

        for (subscription_entity,) in subscription_entities:
            async with session_maker() as database_session:
                polygon = Polygon(
                    map(
                        lambda x: (x.latitude, x.longitude),
                        subscription_entity.subscription_vertices,
                    )
                )

                subscription_entity_matches_fire_locations = set()

                for (
                    subscription_match_entity
                ) in subscription_entity.subscription_matches:
                    for (
                        subscription_match_fire_location_entity
                    ) in subscription_match_entity.subscription_match_fire_locations:
                        subscription_entity_matches_fire_locations.add(
                            subscription_match_fire_location_entity.fire_location_id
                        )

                subscription_match_entity = SubscriptionMatchEntity()
                subscription_entity.subscription_matches.append(
                    subscription_match_entity
                )

                for (fire_location_entity,) in fire_location_entities:
                    fire_location_point = Point(
                        fire_location_entity.latitude,
                        fire_location_entity.longitude,
                    )

                    if (
                        fire_location_entity.id
                        not in subscription_entity_matches_fire_locations
                        and polygon.contains(fire_location_point)
                    ):
                        subscription_match_entity.subscription_match_fire_locations.append(
                            SubscriptionMatchFireLocationEntity(
                                fire_location_id=fire_location_entity.id
                            )
                        )

                        print("Match!")

                database_session.add(subscription_entity)
                await database_session.commit()
