from __future__ import annotations

import json
from typing import TYPE_CHECKING, Callable, Iterable, Literal, Protocol, TypedDict, assert_never

from attrs import define
from botocore.exceptions import ClientError
from result import Err, Ok, Result, as_result

from ..cloudformation import CloudFormationClient

if TYPE_CHECKING:
    from mypy_boto3_cloudformation.type_defs import DescribeTypeOutputTypeDef

type Permission = str


class Handler(TypedDict):
    permissions: list[Permission]
    timeoutInMinutes: int


class HandlerTypes(TypedDict):
    create: Handler
    update: Handler
    delete: Handler
    read: Handler
    list: Handler


PermissionsLevels = {
    "read": {"read", "list"},
    "modify": {"read", "list", "update", "create"},
    "full": {"read", "list", "update", "create", "delete"},
}


class ResourceProviderSchema(TypedDict):
    handlers: HandlerTypes
    documentationUrl: str


class ResourceInformationResolverProtocol(Protocol):
    client: CloudFormationClient

    def resolve(self, resource_type: str, permission_level: str) -> Result[frozenset[Permission], LookupError]: ...


class DefaultDictKey[K, V](dict[K, V]):
    """Implementation of defaultdict that passes the missing key as an input to the default_factory"""

    def __init__(self, default_factory: Callable[[K], V]):
        super().__init__()
        self.default_factory = default_factory

    def __missing__(self, key: K) -> V:
        if self.default_factory is None:
            raise KeyError(key)

        value = self[key] = self.default_factory(key)
        return value


@define
class ResourceInformationResolver(ResourceInformationResolverProtocol):
    client: CloudFormationClient

    @staticmethod
    def _is_module(resource_type_name: str):
        return resource_type_name.endswith("MODULE")

    def __attrs_post_init__(self):
        self.resource_schemas = DefaultDictKey[str, Result[ResourceProviderSchema, str]](self._resolve_resource_schema)

    def _load_module_schema(
        self, resource_type: DescribeTypeOutputTypeDef
    ) -> Result[ResourceProviderSchema, json.JSONDecodeError]:
        schema = resource_type["Schema"]
        result: Result[ResourceProviderSchema, json.JSONDecodeError] = as_result(json.JSONDecodeError)(json.loads)(
            schema
        )
        return result

    def _describe_type(
        self, resource_type_name: str, resource_type: Literal["RESOURCE", "MODULE"] = "RESOURCE"
    ) -> Result[DescribeTypeOutputTypeDef, ClientError]:
        return as_result(ClientError)(self.client.describe_type)(Type=resource_type, TypeName=resource_type_name)

    def _resolve_resource_schema(self, resource_type_name: str) -> Result[ResourceProviderSchema, str]:
        resource_type = "RESOURCE" if not self._is_module(resource_type_name) else "MODULE"
        return (
            self._describe_type(resource_type=resource_type, resource_type_name=resource_type_name)
            .and_then(self._load_module_schema)
            .map_err(str)
        )

    def _get_permissions_for_operation(self, handler: Handler) -> Result[Iterable[Permission], LookupError]:
        if not (permissions := handler.get("permissions")):
            return Err(LookupError("Permissions Unavailable"))
        return Ok(permissions)

    def resolve(self, resource_type: str, permission_level: str) -> Result[frozenset[Permission], LookupError]:
        schema_result = self.resource_schemas[resource_type]
        match schema_result:
            case Ok(schema):
                if not (handlers := schema.get("handlers")):
                    return Err(LookupError(f"Handler Information Not Found {resource_type}"))

                permissions = set[Permission]()
                handlers_for_permission_level = PermissionsLevels.get(permission_level, [])
                for handler_type, handler in handlers.items():
                    if handler_type in handlers_for_permission_level:
                        self._get_permissions_for_operation(handler).and_then(permissions.update)
                return Ok(frozenset(permissions))

            case Err():
                return Err(LookupError(f"Schema Not Found {resource_type}"))

            case _:
                assert_never(schema_result)
