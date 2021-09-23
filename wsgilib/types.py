"""Common types."""

from typing import Callable, Iterable, NamedTuple, Optional, Union

from flask import Response


__all__ = [
    'ETag',
    'Header',
    'Message',
    'Quality',
    'Route',
]


ETag = Union[bool, str]
Header = tuple[str, str]
Message = Union[str, bytes]
Quality = tuple[str, float]


class Route(NamedTuple):
    """A REST route information."""

    methods: Union[Iterable[str], str]
    route: str
    function: Callable[Exception, Response]
    endpoint: Optional[str] = None
