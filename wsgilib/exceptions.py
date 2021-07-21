"""Common Exceptions:"""


__all__ = ['InvalidData']


class InvalidData(Exception):
    """Indicates invalid data."""

    def __init__(self, expected: type, received: type):
        super().__init__()
        self.expected = expected
        self.received = received

    def __str__(self):
        """Returns an error message."""
        return (
            f'Expected data of type "{self.expected}", '
            f'but got {self.received}".')
