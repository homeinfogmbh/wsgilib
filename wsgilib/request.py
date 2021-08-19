"""Request parsing."""

from typing import Iterator

from flask import request
from werkzeug.local import LocalProxy

from wsgilib.types import Quality


__all__ = ['ACCEPT']


def split_quality(string: str) -> Quality:
    """Splits an optional quality parameter
    q=<float> from the provided string.
    """

    try:
        string, quality = string.split(';')
    except ValueError:
        return (string, 1)

    try:
        _, quality = quality.split('=')
        quality = float(quality)
    except ValueError:
        return (string, 1)

    return (string, quality)


def split_csv(string: str) -> Iterator[Quality]:
    """Yields the respective elements."""

    for item in string.split(','):
        if item:
            yield split_quality(item)


def get_accept() -> dict[str, float]:
    """Yields accepting types."""

    return dict(split_csv(request.headers.get('Accept', '')))


ACCEPT = LocalProxy(get_accept)
