"""Paging of iterables."""

from typing import Iterable, NamedTuple, Union

from flask import request

from wsgilib.types import Page


__all__ = ['PageInfo', 'Browser']


class PageInfo(NamedTuple):
    """Represents page information."""

    full_pages: int
    remainder: int

    @property
    def pages(self):
        """Returns the amount of pages to be expected."""
        return self.full_pages + (self.remainder > 0)

    def to_json(self):
        """Returns a JSON representation of the page information."""
        return {
            'fullPages': self.full_pages,
            'remainder': self.remainder,
            'pages': self.pages
        }


class Browser:
    """Page browser."""

    def __init__(self, *, page_arg: str = 'page', size_arg: str = 'size',
                 info_arg: str = 'pages', default_page: int = 0,
                 default_size: int = 10):
        """Sets the paging configuration."""
        self.page_arg = page_arg
        self.size_arg = size_arg
        self.info_arg = info_arg
        self.default_page = default_page
        self.default_size = default_size

    def __call__(self, iterable: Iterable) -> Union[PageInfo, Page]:
        """Returns the browsed real estates or page info."""
        if self.info:
            return self.pages(iterable)

        return self.browse(iterable)

    @property
    def page(self) -> int:
        """Returns the page."""
        return int(request.args.get(self.page_arg, self.default_page))

    @property
    def size(self) -> int:
        """Returns the page size."""
        return int(request.args.get(self.size_arg, self.default_size))

    @property
    def info(self) -> bool:
        """Returns the page size."""
        return self.info_arg in request.args

    @property
    def wanted(self) -> bool:
        """Determines if browsing has been requested by URL parameters."""
        return any(
            (self.page_arg in request.args, self.size_arg in request.args,
             self.info)
        )

    def browse(self, iterable: Iterable) -> Page:
        """Pages the respective iterable."""
        size = self.size
        first = self.page * size
        last = first + size -1

        for index, item in enumerate(iterable):
            if index < first:
                continue

            if index > last:
                break

            yield item

    def pages(self, iterable: Iterable) -> PageInfo:
        """Counts the amount of pages."""
        size = self.size
        items = 0

        for items, _ in enumerate(iterable, start=1):
            pass

        return PageInfo(items // size, items % size)
