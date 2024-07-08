from types import MappingProxyType
from typing import Any, Protocol, Type, get_type_hints

from attrs import frozen
from result import Result

from ..domain.queries import Query


class DuplicateHandlerError(KeyError):
    pass


class HandlerRegistry[K: Type[Query], V: Type[QueryHandler]](dict[K, V]):
    def __setitem__(self, _type: K, handler: V):
        if _type in self:
            raise DuplicateHandlerError(
                f"{_type.__name__} already registered to "
                f"Handler: {self[_type].__name__}, "
                f"Can't overwrite to {handler.__name__}. "
                f"Update 'query' in {handler.__call__.__qualname__} "
                f"to a distinct Type"
            )
        super().__setitem__(_type, handler)


@frozen
class QueryHandler(Protocol):
    __registry = HandlerRegistry[type[Query], type["QueryHandler"]]()
    registry = MappingProxyType(__registry)

    @classmethod
    def __attrs_init_subclass__(cls) -> None:
        _type = get_type_hints(cls.__call__)["query"]
        QueryHandler.__registry[_type] = cls

    def __call__(self, query: Any) -> Result[object, object]: ...
