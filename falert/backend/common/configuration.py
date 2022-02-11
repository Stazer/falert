from typing import Mapping, Any
from os import getenv

from marshmallow import Schema, post_load
from marshmallow.fields import String
from dotenv import load_dotenv


class Configuration:
    def __init__(self, database_url: str) -> None:
        self.__database_url = database_url

    @property
    def database_url(self) -> str:
        return self.__database_url


class ConfigurationSchema(Schema):
    database_url = String(required=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(self, values: Mapping[str, Any], **_kwargs) -> Configuration:
        return Configuration(**values)


def load_from_environment() -> Configuration:
    load_dotenv()

    return ConfigurationSchema().load(
        dict(
            map(
                lambda key: (key, getenv(key.upper())),
                vars(ConfigurationSchema)["_declared_fields"].keys(),
            )
        )
    )
