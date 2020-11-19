"""Common types."""

from datetime import date, time, datetime
from typing import Callable, Generator, Iterable, NamedTuple, Tuple, Union


__all__ = [
    'DateTimeDatetime',
    'ErrorHandler',
    'ETag',
    'ExtendedRoute',
    'Header',
    'Message',
    'Page',
    'Quality',
    'Route',
    'SimpleRoute'
]


DateTimeDatetime = Union[date, time, datetime]
ErrorHandler = Tuple[Exception, Callable]
ETag = Union[bool, str]
Header = Tuple[str, str]
Message = Union[str, bytes]
Page = Generator[object, None, None]
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
