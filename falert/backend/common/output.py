from uuid import UUID
from typing import List, Any, Optional, Mapping

from marshmallow import Schema, fields, post_load


class BaseOutput:
    pass


class TriggerMatchingOutput(BaseOutput):
    def __init__(
        self,
        dataset_harvest_ids: Optional[List[UUID]] = None,
        subscription_ids: Optional[List[UUID]] = None,
    ):
        super().__init__()

        self.__dataset_harvest_ids = dataset_harvest_ids
        self.__subscription_ids = subscription_ids

    @property
    def dataset_harvest_ids(self) -> Optional[List[UUID]]:
        return self.__dataset_harvest_ids

    @property
    def subscription_ids(self) -> Optional[List[UUID]]:
        return self.__subscription_ids


class TriggerMatchingOutputSchema(Schema):
    subscription_ids = fields.List(fields.UUID(), allow_none=True)
    dataset_harvest_ids = fields.List(fields.UUID(), allow_none=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> TriggerMatchingOutput:
        return TriggerMatchingOutput(**values)


class TriggerNotifyingOutput(BaseOutput):
    def __init__(
        self,
        subscription_match_ids: Optional[List[UUID]],
    ):
        super().__init__()

        self.__subscription_match_ids = subscription_match_ids

    @property
    def subscription_match_ids(self) -> Optional[List[UUID]]:
        return self.__subscription_match_ids


class TriggerNotifyingOutputSchema(Schema):
    subscription_match_ids = fields.List(fields.UUID(), allow_none=True)

    # pylint: disable=no-self-use
    @post_load
    def _on_post_load(
        self, values: Mapping[str, Any], **_kwargs
    ) -> TriggerNotifyingOutput:
        return TriggerNotifyingOutput(**values)
