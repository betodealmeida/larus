from enum import Enum


class Button:

    """
    Class used to describe a button in the Launchpad Mini.

    A button in the top row:

        >>> Button(5)

    A button in the right column:

        >>> Button('B')

    A button in the grid:

        >>> Button(1, 8)

    A combination of buttons:

        >>> button = Button('H') + Button(1)

    """

    def __init__(self, *values):
        pass


class Row:
    pass


class Column:
    pass


class Grid:
    pass


class Color(Enum):
    OFF = 12
    LOW_RED = 13
    FULL_RED = 15
    LOW_AMBER = 29
    FULL_AMBER = 63
    FULL_YELLOW = 62
    LOW_GREEN = 28
    FULL_GREEN = 60

    @property
    def double(self):
        self.value
