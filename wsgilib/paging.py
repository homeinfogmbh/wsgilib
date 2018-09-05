# Copyright 2017 HOMEINFO - Digitale Informationssysteme GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Paging of iterables."""

from collections import namedtuple

from flask import request


__all__ = ['PageInfo', 'Browser']


class PageInfo(namedtuple('PageInfo', ('full_pages', 'remainder'))):
    """Represents page information."""

    @property
    def pages(self):
        """Returns the amount of pages to be expected."""
        return self.full_pages + self.remainder > 0

    def to_json(self):
        """Returns a JSON representation of the page information."""
        return {
            'fullPages': self.full_pages,
            'remainder': self.remainder,
            'pages': self.pages}


class Browser:
    """Page browser."""

    def __init__(self, page_arg='page', size_arg='size', default_page=0,
                 default_size=10):
        """Sets the paging configuration."""
        self.page_arg = page_arg
        self.size_arg = size_arg
        self.default_page = default_page
        self.default_size = default_size

    @property
    def page(self):
        """Returns the page."""
        return int(request.args.get(self.page_arg, self.default_page))

    @property
    def size(self):
        """Returns the page size."""
        return int(request.args.get(self.size_arg, self.default_size))

    def browse(self, iterable):
        """Pages the respective iterable."""
        first = self.page * self.size
        last = first + self.size -1

        for index, item in enumerate(iterable):
            if index < first:
                continue

            if index > last:
                break

            yield item


    def pages(self, iterable):
        """Counts the amount of pages."""
        items = 0

        for items, _ in enumerate(iterable):
            pass

        return PageInfo(items // self.size, items % self.size)
