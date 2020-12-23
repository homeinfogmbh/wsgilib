"""Common types."""

from typing import Callable, Iterable, NamedTuple, Tuple, Union


__all__ = [
    'ETag',
    'Header',
    'Message',
    'Quality',
    'Route',
]


ETag = Union[bool, str]
Header = Tuple[str, str]
Message = Union[str, bytes]
Quality = Tuple[str, float]


class Route(NamedTuple):
    """A REST route information."""

    methods: Iterable[str]
    route: str
    function: Callable
