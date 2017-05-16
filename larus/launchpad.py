from enum import Enum
import re
import struct
from typing import Match, Sequence

import _cffi_backend


class Event:
    """
    An event from the launchpad.

    """
    def match(self, indata: _cffi_backend.buffer) -> bool:
        """
        Return true if indata matches the event.

        For now, this only supports "note on" events. In the future it will
        be expanded to receive a context and track button combinations and
        button clicks ("note on" followed by "note off").

        """
        raise NotImplementedError('Subclasses must implement match')


class Button(Event):
    """
    Class used to describe a button in the Launchpad Mini.

    A button in the top row:

        >>> Button('6')

    A button in the right column:

        >>> Button('B')

    A button in the grid:

        >>> Button('1A')

    """

    def __init__(self, code: str) -> None:
        m: Match[str] = re.match('^([1-8])?([A-H])?$', code)
        if not m or not len(code):
            raise Exception(
                'Button spec should be a string representing a button, eg: '
                '"1", "B" or "3H".'
            )
        groups: Sequence[str] = m.groups()
        self.x: Optional[int] = groups[0]
        if self.x is None:
            self.x = 8
        else:
            self.x = int(self.x) - 1
        self.y: Optional[int] = groups[1]
        if self.y is None:
            self.y = 8
        else:
            # y is 0 at the bottom, H
            self.y = 'HGFEDCBA'.index(groups[1])

        # compute the pitch expected from this button
        self.pitch: int = self.get_pitch()

    def get_pitch(self) -> int:
        """
        Return the pitch expected for this button.

        When one of these buttons from the grid or from the colum nis pressed
        the Launchpad will send on note on and note off:

            144 0-120 127  # note on
            128 0-120 64   # note off

        When the top row is pressed the Launchpad sends a CC:

            176 104-111 127
            176 104-111 0

        """
        if self.y == 8:
            return 104 + self.x
        else:
            return (7 - self.y) * 16 + self.x

    def match(self, indata) -> bool:
        if len(indata) == 3:
            status, pitch, vel = struct.unpack('3B', indata)
            if status == 144:
                return pitch == self.pitch
            elif status == 176:
                return pitch == self.pitch

        return False

    def get_event(self, indata):
        if self.match(indata):
            return self

        raise Exception('Button does not match `indata`.')


class Buttons(Event):
    def __init__(self, buttons):
        self.buttons = buttons

    def match(self, indata):
        return any(button.match(indata) for button in self.buttons)

    def get_event(self, indata):
        for button in self.buttons:
            if button.match(indata):
                return button

        raise Exception('No button matches `indata`.')


Grid = Buttons([Button(f'{i}{c}') for i in range(1, 9) for c in 'ABCDEFGH'])
Column = Buttons([Button(c) for c in 'ABCDEFGH'])
Grid = Buttons([Button(str(i)) for i in range(1, 9)])


class Note(Enum):
    OFF = 12
    LOW_RED = 13
    FULL_RED = 15
    LOW_AMBER = 29
    FULL_AMBER = 63
    FULL_YELLOW = 62
    LOW_GREEN = 28
    FULL_GREEN = 60


class Color(Enum):
    OFF = 0.0
    LOW_GREEN = 0.125
    FULL_GREEN = 0.25
    FULL_YELLOW = 0.375
    LOW_AMBER = 0.5
    FULL_AMBER = 0.625
    LOW_RED = 0.75
    FULL_RED = 0.875
