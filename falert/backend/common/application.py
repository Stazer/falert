from asyncio import run


class BaseApplication:
    pass


class AsynchronousApplication(BaseApplication):
    @classmethod
    def run(cls):
        run(cls().main())

    async def main(self):
        raise NotImplementedError()
