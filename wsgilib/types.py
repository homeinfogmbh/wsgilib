"""Common types."""

from typing import Callable, Iterable, NamedTuple, Tuple, Union


__all__ = [
    'ErrorHandler',
    'ETag',
    'ExtendedRoute',
    'Header',
    'Message',
    'Quality',
    'Route',
    'SimpleRoute'
]


ErrorHandler = Tuple[Exception, Callable]
ETag = Union[bool, str]
Header = Tuple[str, str]
Message = Union[str, bytes]
Quality = Tuple[str, float]


class SimpleRoute(NamedTuple):
    """Simple flask route information."""

    methods: Iterable[str]
    route: str
    function: Callable


class ExtendedRoute(NamedTuple):
    """An extended route with additional endpoint information."""

    methods: Iterable[str]
    route: str
    function: Callable
    endpoint: str


Route = Union[SimpleRoute, ExtendedRoute]
