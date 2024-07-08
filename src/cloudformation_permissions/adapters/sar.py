import fnmatch
import json
import pathlib
from functools import cache, cached_property
from types import MappingProxyType
from typing import Literal, Mapping, Protocol, Sequence, TypedDict

type AccessLevel = Literal["List", "Read", "Write", "Permissions Management", "Tagging"]


class ActionResourceType(TypedDict):
    resourceType: str
    required: bool
    conditionKeys: list[str]
    dependentActions: list[str]


class ServiceConditionKeys(TypedDict):
    name: str
    referenceHref: str
    description: str
    type: str


class ServiceResourceType(TypedDict):
    name: str
    referenceHref: str
    arnPattern: str
    conditionKeys: list[ServiceConditionKeys]


class Action(TypedDict):
    name: str
    permissionOnly: bool
    referenceHref: str
    description: str
    accessLevel: AccessLevel
    resourceTypes: list[ActionResourceType]
    conditionKeys: list[str]


type QualifiedName = str
type ActionPattern = str


class QualifiedAction(Action):
    qualifiedName: QualifiedName


class Service(TypedDict):
    name: str
    servicePrefix: str
    authReferenceHref: str
    apiReferenceHref: str
    actions: list[Action]
    resourceTypes: list[ServiceResourceType]


type ServiceAuthorizationReference = list[Service]


class ServiceAuthorizationReferenceProcotol(Protocol):
    def list_actions_by_pattern(self, pattern: ActionPattern) -> Sequence[QualifiedAction]: ...


class ServiceAuthorizationReferenceLocal(ServiceAuthorizationReferenceProcotol):
    def __init__(self, path: pathlib.Path):
        self.index: ServiceAuthorizationReference = json.loads(path.read_text())
        self.list_actions_by_pattern = cache(self._list_actions_by_pattern)

    @cached_property
    def actions(self) -> Mapping[QualifiedName, QualifiedAction]:
        _actions: dict[QualifiedName, QualifiedAction] = {}
        for service in self.index:
            for action in service["actions"]:
                _name = f"{service['servicePrefix']}:{action['name']}"
                _actions[_name] = QualifiedAction(**action, qualifiedName=_name)
        return MappingProxyType(_actions)

    def _list_actions_by_pattern(self, pattern: ActionPattern) -> list[QualifiedAction]:
        return [self.actions[action] for action in fnmatch.filter(self.actions.keys(), pattern)]
