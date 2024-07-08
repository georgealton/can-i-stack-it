from enum import StrEnum, auto
from pathlib import Path
from typing import ClassVar, NewType, Self

from attrs import define, field, frozen


@frozen
class ARN:
    partition: str
    service: str
    region: str
    account_id: str
    resource: str

    delimiter: ClassVar[str] = ":"
    domain: ClassVar[str] = "arn"

    @classmethod
    def from_str(cls, arn_str: str) -> Self:
        split = arn_str.split(cls.delimiter, maxsplit=6)
        return cls(*split[1:])

    def __str__(self):
        return self.delimiter.join(
            (
                self.domain,
                self.partition,
                self.service,
                self.region,
                self.account_id,
                self.resource,
            )
        )


class Authorized(StrEnum):
    ALLOWED = auto()
    DENIED = auto()
    UNKNOWN = auto()


ResourceTypeName = str
Action = NewType("Action", str)


@define
class ActionPermission:
    action: Action
    authorization: Authorized = field(default=Authorized.UNKNOWN)


@frozen
class ShortResourceInfo:
    TypeName: str
    LogicalId: str


@frozen
class ResourcePermissionSummary:
    resource_type: ResourceTypeName
    permissions: list[ActionPermission]


@frozen
class TemplateSummary:
    source: ARN | Path
    resources: dict[str, ResourcePermissionSummary]
