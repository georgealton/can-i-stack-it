from pathlib import Path

from attrs import frozen

from .model import ARN


class Query: ...


@frozen
class ListResourceTypePermissions(Query):
    ResourceType: str
    PermissionLevel: str


@frozen
class VerifyResourceTypePermissions(Query):
    ResourceType: str
    Role: ARN | None
    PermissionLevel: str


@frozen
class ListTemplatePermissions(Query):
    TemplateSource: ARN | Path
    PermissionLevel: str


@frozen
class VerifyTemplatePermissions(Query):
    TemplateSource: ARN | Path
    Role: ARN | None
    PermissionLevel: str
