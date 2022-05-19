"""Convenience functions to get specific data types from request args."""

from contextlib import suppress
from datetime import datetime
from re import search
from typing import IO, Iterator, Optional

from flask import request, Response, stream_with_context

from mimeutil import mimetype


__all__ = ['get_bool', 'get_datetime', 'get_int', 'get_range', 'filestream']


BOOL_STRINGS = {
    'yes': True,
    'true': True,
    'on': True,
    'no': False,
    'false': False,
    'off': False
}


def get_bool(key: str, default: bool = False) -> bool:
    """Returns a boolean from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    with suppress(ValueError, TypeError):
        return bool(int(value))

    try:
        return BOOL_STRINGS[value.casefold()]
    except KeyError:
        raise ValueError('Not a boolean:', key, value) from None


def get_datetime(
        key: str,
        default: Optional[datetime] = None
) -> Optional[datetime]:
    """Returns a datetime from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    return datetime.fromisoformat(value)


def get_int(key: str, default: Optional[int] = None) -> Optional[int]:
    """Returns a boolean from the request args."""

    try:
        value = request.args[key]
    except KeyError:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        raise ValueError('Not an int:', key, value) from None


def get_range() -> tuple[int, Optional[int]]:
    """Gets the requested stream range."""

    if not (range_ := request.headers.get('Range')):
        return 0, None

    match = search(r'(\d+)-(\d*)', range_)
    start, end = match.groups()
    start = int(start) if start else 0
    end = int(end) if end else None
    return start, end


def iter_file(file: IO, *, chunk_size: int = 4096) -> Iterator[bytes]:
    """Yields chunks of a file."""

    while chunk := file.read(chunk_size):
        yield chunk


def filestream(file: IO, *, chunk_size: int = 4096) -> Response:
    """Returns a file stream."""

    content_type = mimetype(file)
    file.seek(0)

    return Response(
        stream_with_context(iter_file(file, chunk_size=chunk_size)),
        content_type=content_type
    )
