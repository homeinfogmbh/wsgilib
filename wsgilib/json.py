"""JSON parsing and serialization."""

from contextlib import suppress
from datetime import datetime, date, time
from types import GeneratorType
from typing import Callable, Union
import html
import json


__all__ = ['dumps', 'escape', 'loads']


def escape(obj: object) -> object:
    """Escapes HTML code withtin the provided object."""

    if isinstance(obj, str):
        return html.escape(obj)

    if isinstance(obj, list):
        return [escape(item) for item in obj]

    if isinstance(obj, dict):
        return {key: escape(value) for key, value in obj.items()}

    return obj


def jsonify(obj: object) -> object:
    """Encodes the object into a JSON-ish value."""

    if isinstance(obj, (date, time, datetime)):
        return obj.isoformat()

    if isinstance(obj, (set, frozenset, GeneratorType)):
        return tuple(obj)

    return obj


def parse_str(string: str) -> Union[date, time, datetime]:
    """Parses further python objects from a str."""

    with suppress(ValueError):
        return date.fromisoformat(string)

    with suppress(ValueError):
        return time.fromisoformat(string)

    with suppress(ValueError):
        return datetime.fromisoformat(string)

    raise ValueError('Not a datetime, date or time string.')


def decode(dictionary: dict) -> dict:
    """Decodes the JSON-ish dictionary values."""

    for key, value in dictionary.items():
        if isinstance(value, str):
            with suppress(ValueError):
                dictionary[key] = parse_str(value)

    return dictionary


def dumps(obj: object, *, default: Callable = jsonify, **kwargs) -> str:
    """Overrides json.dumps."""

    return json.dumps(obj, default=default, **kwargs)


def loads(string: str, *, object_hook: Callable = decode, **kwargs) -> object:
    """Overrides json.loads."""

    return json.loads(string, object_hook=object_hook, **kwargs)
