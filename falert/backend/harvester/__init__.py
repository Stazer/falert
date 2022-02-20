from csv import DictReader
from asyncio import gather
from tempfile import NamedTemporaryFile

from aiohttp import ClientSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, joinedload

from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.output import (
    TriggerMatchingOutput,
    TriggerMatchingOutputSchema,
)
from falert.backend.common.entity import (
    BaseEntity,
    DatasetEntity,
    FireLocationEntity,
    DatasetHarvestEntity,
)
from falert.backend.common.input import NASAFireLocationInputSchema
from falert.backend.common.messenger import AsyncpgSender, Sender


class BaseHarvester:
    pass


class NASAHarvester(BaseHarvester):
    def __init__(
        self, engine: AsyncEngine, sender: Sender, url: str, chunk_size: int = 8192
    ):
        super().__init__()

        self.__engine = engine
        self.__sender = sender
        self.__url = url
        self.__chunk_size = chunk_size

    @property
    def url(self) -> str:
        return self.__url

    @property
    def chunk_size(self) -> int:
        return self.__chunk_size

    # pylint: disable=too-many-locals
    async def run(self):
        session_maker = sessionmaker(
            self.__engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with session_maker() as database_session:
            result = await database_session.execute(
                select(DatasetEntity)
                .options(
                    joinedload(DatasetEntity.dataset_harvests).joinedload(
                        DatasetHarvestEntity.fire_locations
                    )
                )
                .where(DatasetEntity.url == self.url)
            )

            dataset_entity = list(result.unique())[0]
            reported_fire_locations = {}

            if dataset_entity is None:
                dataset_entity = DatasetEntity(url=self.url)
            else:
                dataset_entity = dataset_entity[0]

                for dataset_harvest_entity in dataset_entity.dataset_harvests:
                    for fire_location in dataset_harvest_entity.fire_locations:
                        reported_fire_locations[
                            (
                                fire_location.latitude,
                                fire_location.longitude,
                                fire_location.acquired,
                            )
                        ] = fire_location

            dataset_harvest_entity = DatasetHarvestEntity()

            async with ClientSession() as client_session:
                async with client_session.get(self.url) as response:
                    with NamedTemporaryFile() as write_file:
                        async for data in response.content.iter_chunked(
                            self.chunk_size
                        ):
                            write_file.write(data)

                        write_file.flush()

                        with open(write_file.name, "r", encoding="utf-8") as read_file:
                            reader = DictReader(read_file)

                            for row in reader:
                                fire_location_input = (
                                    NASAFireLocationInputSchema().load(row)
                                )

                                if (
                                    fire_location_input.latitude,
                                    fire_location_input.longitude,
                                    fire_location_input.acquired,
                                ) not in reported_fire_locations:
                                    dataset_harvest_entity.fire_locations.append(
                                        FireLocationEntity(
                                            latitude=fire_location_input.latitude,
                                            longitude=fire_location_input.longitude,
                                            raw=row,
                                            acquired=fire_location_input.acquired,
                                        )
                                    )

            dataset_entity.dataset_harvests.append(dataset_harvest_entity)
            database_session.add(dataset_entity)
            await database_session.commit()

            trigger_matching_output = TriggerMatchingOutput(
                dataset_harvest_ids=[
                    dataset_harvest_entity.id,
                ],
            )

            await self.__sender.send(
                "trigger_matching",
                TriggerMatchingOutputSchema().dumps(
                    trigger_matching_output,
                ),
            )


class Application(AsynchronousApplication):
    def __init__(self):
        super().__init__()

        self.__sender = None

    async def main(self):
        async with self._engine.begin() as connection:
            raw_connection = await connection.get_raw_connection()

            self.__sender = AsyncpgSender(
                raw_connection.dbapi_connection.driver_connection
            )

        harvester0 = NASAHarvester(
            self._engine,
            self.__sender,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv",
        )

        harvester1 = NASAHarvester(
            self._engine,
            self.__sender,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv",
        )

        harvester2 = NASAHarvester(
            self._engine,
            self.__sender,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv",
        )

        await gather(
            harvester0.run(),
            harvester1.run(),
            harvester2.run(),
        )
