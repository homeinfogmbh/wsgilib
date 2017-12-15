"""Post data converter functions with caching."""

from functools import lru_cache

from wsgilib.json import json_loads

__all__ = ['bytes_to_text', 'text_to_json', 'text_to_dom']


@lru_cache(maxsize=1)
def bytes_to_text(bytes_):
    """Converts bytes to text."""

    return bytes_.decode()


@lru_cache(maxsize=1)
def text_to_json(text):
    """Converts text into a JSON object."""

    return json_loads(text)


@lru_cache(maxsize=1)
def text_to_dom(dom, text):
    """Converts text into a JSON object."""

    return dom.CreateFromDocument(text)
