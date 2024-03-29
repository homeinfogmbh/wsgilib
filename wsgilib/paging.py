"""Paging of iterables."""

from itertools import islice
from typing import Iterable, Iterator, NamedTuple, Union

from flask import request


__all__ = ["PageInfo", "Browser"]


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
            "fullPages": self.full_pages,
            "remainder": self.remainder,
            "pages": self.pages,
        }


class Browser:
    """Page browser."""

    def __init__(
        self,
        *,
        page_arg: str = "page",
        size_arg: str = "size",
        info_arg: str = "pages",
        default_page: int = 0,
        default_size: int = 10
    ):
        """Sets the paging configuration."""
        self.page_arg = page_arg
        self.size_arg = size_arg
        self.info_arg = info_arg
        self.default_page = default_page
        self.default_size = default_size

    def __call__(self, iterable: Iterable) -> Union[PageInfo, Iterator]:
        """Returns the browsed real estates or page info."""
        return self.pages(iterable) if self.info else self.browse(iterable)

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
            [self.page_arg in request.args, self.size_arg in request.args, self.info]
        )

    def browse(self, iterable: Iterable) -> Iterator:
        """Pages the respective iterable."""
        first = self.page * self.size
        return islice(iterable, first, first + self.size)

    def pages(self, iterable: Iterable) -> PageInfo:
        """Counts the amount of pages."""
        return PageInfo(*divmod(sum(1 for _ in iterable), self.size))
