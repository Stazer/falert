from falert.backend.common.application import AsynchronousApplication
from falert.backend.common.messenger import AsyncpgReceiver


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
