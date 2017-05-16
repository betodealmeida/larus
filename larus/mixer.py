# -*- coding: utf-8 -*-

"""
Larus mixer

This is a 8-track mixer that displays levels in the Launchpad Mini, and whose
individual levels can be controlled from the grid. It also allows toggling the
mute state of individual tracks or all of them.

The mixer mode is selected by pressing button 5 in the top row of the Launchpad
Mini.

"""

import numpy as np

import jack

from launchpad import Button, Color, Column, Grid
from modes import Mode


# create an array of colors where the bottom is LOW_GREEN and the top is
# FULL_RED, in order to display the levels of each track
palette = np.linspace(Color.LOW_GREEN, Color.FULL_RED, 8)
meter = np.ones((8, 8), np.float64) * palette.reshape(8, 1)


class Mixer(Mode):

    # the mixer mode is activated by pressing button #5 in the top row
    select: Button = Button('5')

    def __init__(self, client: jack.Client) -> None:
        super().__init__(client)

        # the level of each of the 8 tracks; start at 66%
        self.levels = np.ones(8, np.float64) * 0.66

        # muted state
        self.muted = np.zeros(8, np.bool)

        # arrays representing data in the Launchpad Mini buttons
        self.grid = np.zeros((8, 8), np.float64)
        self.row = np.zeros(8, np.float64)
        self.column = np.zeros(8, np.float64)

    def register_ports(self) -> None:
        """
        Register 8 input tracks and 2 output tracks.

        """
        # create 4 stereo input tracks
        self.inports = [
            self.client.inports.register(f'input_{track}_{channel}')
            for track in (1, 2, 3, 4)
            for channel in (1, 2)
        ]

        # create 1 stereo output track
        self.outports = [
            self.client.outports.register(f'output_{channel}')
            for channel in (1, 2)
        ]

    @Mode.process_audio
    def mix_audio(self, in_, out) -> None:
        """
        Mix incoming audio.

        """
        adjusted = in_ * self.levels * ~self.muted
        out[:, 0] = np.average(adjusted[:, 0::2], 1)
        out[:, 1] = np.average(adjusted[:, 1::2], 1)

        amplitude = np.average(out, 0)
        self.grid = meter[:]
        self.grid[amplitude < meter] = 0

    @Mode.process_midi(Grid)
    def adjust_level(self, button):
        """
        Adjust the level for a track when a button is pressed in the grid.

        If the bottom button is pressed we toggle the mute state for the track.

        """
        if button.y == 0:
            # toggle mute
            self.muted[button.x] = ~self.muted[button.x]
        else:
            level = np.linspace(0, 1, 8)[button.y]
            self.levels[button.x] = level

    @Mode.process_midi(Column)
    def adjust_levels(self, button):
        """
        Adjust levels for all tracks.

        The bottom button (H) toggles the mute state of all tracks.

        """
        if button.y == 0:
            # toggle mute
            self.muted = ~self.muted
        else:
            level = np.linspace(0, 1, 8)[button.y]
            self.levels[:] = level
