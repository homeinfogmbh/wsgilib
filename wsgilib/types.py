"""Common types."""

from datetime import datetime
from typing import Callable, Iterable, NamedTuple, Optional, Protocol, Union

from flask import Response


__all__ = [
    'CORSType',
    'ETag',
    'Header',
    'Message',
    'Quality',
    'Route',
    'Session'
]


CORSType = Union[Callable, dict, bool]
ETag = Union[bool, str]
Header = tuple[str, str]
Message = Union[str, bytes]
Quality = tuple[str, float]


class Route(NamedTuple):
    """A REST route information."""

    methods: Union[Iterable[str], str]
    route: str
    function: Callable[[Exception], Response]
    endpoint: Optional[str] = None


class Session(Protocol):
    """Session protocol."""

    id: int
    secret: str
    start: datetime
    end: datetime
