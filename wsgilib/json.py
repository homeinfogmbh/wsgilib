"""JSON parsing and serialization."""

from datetime import datetime, date, time
from html import escape
from json import dumps
from types import GeneratorType
from typing import Any


__all__ = ['View', 'htmlescape', 'jsonify']


class View(dict):
    """A JSON view.
    Keys represent attributes to read,
    values represent optional keys of the JSON object.
    If the key is false-ish, the view falls back onto the attribute.
    """

    def __call__(self, model: object) -> dict[str, Any]:
        """Apply the view to the respective model."""
        result = {}

        for attribute, key in self.items():
            if isinstance(key, dict):
                type(self)(key)(getattr(model, attribute))
            else:
                result[key or attribute] = getattr(model, attribute)

        return result


def htmlescape(obj: object) -> object:
    """Escapes HTML within the provided object."""

    if isinstance(obj, str):
        return escape(obj)

    if isinstance(obj, list):
        return [htmlescape(item) for item in obj]

    if isinstance(obj, dict):
        return {key: htmlescape(value) for key, value in obj.items()}

    return obj


def object_to_json(obj: object) -> object:
    """Encodes the object into a JSON-ish value."""

    if isinstance(obj, (date, time, datetime)):
        return obj.isoformat()

    if isinstance(obj, (set, frozenset, GeneratorType)):
        return tuple(obj)

    return obj


def jsonify(obj: object, indent: int = None) -> str:
    """Overrides json.dumps."""

    return dumps(obj, default=object_to_json, indent=indent)
