from typing import List, Union, Any, Dict
from json import loads

from marshmallow import Schema, fields, post_load


class BaseInput:
    @staticmethod
    def on_post_load(schema, values, **_kwargs) -> "BaseInput":
        return schema.constructor(**values)

    @classmethod
    def schema(cls) -> Dict[Any, Any]:
        return {
            "constructor": cls,
            "on_post_load": post_load(cls.on_post_load),
        }

    @classmethod
    def decode(cls, source: Dict[Any, Any]) -> "BaseInput":
        schema = Schema.from_dict(
            {
                **cls.schema(),
            }
        )()

        return schema.load(source)

    @classmethod
    def decode_json(cls, source: Union[str, bytes]):
        return cls.decode(loads(source))


class SubscriptionVertexInput(BaseInput):
    @classmethod
    def schema(cls) -> Dict[Any, Any]:
        return {
            **super().schema(),
            "longitude": fields.Float(required=True),
            "latitude": fields.Float(required=True),
        }

    def __init__(self, longitude: float, latitude: float) -> None:
        super().__init__()

        self.__longitude = longitude
        self.__latitude = latitude

    @property
    def longitude(self) -> float:
        return self.__longitude

    @property
    def latitude(self) -> float:
        return self.__latitude


class SubscriptionInput(BaseInput):
    @classmethod
    def schema(cls) -> Dict[Any, Any]:
        return {
            **super().schema(),
            "vertices": fields.List(
                fields.Nested(
                    Schema.from_dict(SubscriptionVertexInput.schema())(), required=True
                )
            ),
        }

    def __init__(self, vertices: List["SubscriptionVertexInput"]) -> None:
        super().__init__()

        self.__vertices = vertices

    @property
    def vertices(self) -> List["SubscriptionVertexInput"]:
        return self.__vertices
