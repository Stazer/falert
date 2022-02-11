from csv import DictReader
from tempfile import NamedTemporaryFile

from aiohttp import ClientSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.entity import BaseEntity, DatasetEntity, FireLocationEntity
from falert.backend.common.input import NASAFireLocationInputSchema
from falert.backend.common.messenger import AsyncpgSender


class BaseHarvester:
    pass


class NASAHarvester(BaseHarvester):
    def __init__(self, engine: AsyncEngine, url: str, chunk_size: int = 8192):
        super().__init__()

        self.__engine = engine
        self.__url = url
        self.__chunk_size = chunk_size

    @property
    def url(self) -> str:
        return self.__url

    @property
    def chunk_size(self) -> int:
        return self.__chunk_size

    async def run(self):
        session_maker = sessionmaker(
            self.__engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        async with session_maker() as database_session:
            result = await database_session.execute(
                select(DatasetEntity)
                .where(DatasetEntity.url == self.url)
                .options(selectinload(DatasetEntity.fire_locations)),
            )

            dataset_entity = result.fetchone()
            reported_fire_locations = {}

            if dataset_entity is None:
                dataset_entity = DatasetEntity(url=self.url)
            else:
                dataset_entity = dataset_entity[0]
                reported_fire_locations = dict(
                    map(
                        lambda fire_location: (
                            (
                                fire_location.latitude,
                                fire_location.longitude,
                                fire_location.acquired,
                            ),
                            fire_location,
                        ),
                        dataset_entity.fire_locations,
                    )
                )

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
                                    dataset_entity.fire_locations.append(
                                        FireLocationEntity(
                                            latitude=fire_location_input.latitude,
                                            longitude=fire_location_input.longitude,
                                            raw=row,
                                            acquired=fire_location_input.acquired,
                                        )
                                    )

            database_session.add(dataset_entity)
            await database_session.commit()


class Application(AsynchronousApplication):
    def __init__(self):
        super().__init__()

        # pylint: disable=unused-private-member
        self.__sender = None

    async def main(self):
        async with self._engine.begin() as connection:
            raw_connection = await connection.get_raw_connection()

            # pylint: disable=unused-private-member
            self.__sender = AsyncpgSender(
                raw_connection.dbapi_connection.driver_connection
            )

        harvester0 = NASAHarvester(
            self._engine,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_Global_24h.csv",
        )

        harvester1 = NASAHarvester(
            self._engine,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_Global_24h.csv",
        )

        harvester2 = NASAHarvester(
            self._engine,
            # pylint: disable=line-too-long
            "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_Global_24h.csv",
        )

        await harvester0.run()
        await harvester1.run()
        await harvester2.run()
