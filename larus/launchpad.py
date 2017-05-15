from enum import Enum


class Event:
    """
    An event from the launchpad.

    """
    def __call__(self, indata):
        raise NotImplementedError('Subclasses must implement __call__')


class Button(Event):

    """
    Class used to describe a button in the Launchpad Mini.

    A button in the top row:

        >>> Button(5)
        >>> Button('6')

    A button in the right column:

        >>> Button('B')

    A button in the grid:

        >>> Button('1A')

    """

    def __init__(self, code):
        self.x = 
        seld.y = 

    def __call__(self):
        return self

    def __add__(self, other):
        return ButtonCombination()


class Buttons(Event):
    def __init__(self, buttons):
        self.buttons = buttons


class ButtonCombination(Event):
    pass


Grid = Buttons([Button(f'{i}{c}') for i in range(1, 9) for c in 'ABCDEFGH'])
Column = Buttons([Button(c) for c in 'ABCDEFGH'])
Grid = Button([Button(i) for i in range(1, 9)])


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
