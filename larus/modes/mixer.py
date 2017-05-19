# -*- coding: utf-8 -*-

"""
Larus mixer

This is a 8-track mixer that displays levels in the Launchpad Mini, and whose
individual levels can be controlled from the grid. It also allows toggling the
mute state of individual tracks or all of them.

The mixer mode is selected by pressing pad 5 in the top row of the Launchpad
Mini.

"""

import numpy as np

from draw import Color, convert_to_color_array, rapid_led_update
from events import Column, Grid, Press, process_event


# create an array of colors where the bottom is LOW_GREEN and the top is
# FULL_RED, in order to display the levels of each track
palette = np.linspace(1, 0, 9)[:-1]
meter = np.ones((8, 8), np.float64) * palette.reshape(8, 1)


class Mixer:

    # the mixer mode is activated by pressing pad #5 in the top row
    # select: Button = Button('5')

    def __init__(self, client, controlle_deque):
        self.client = client
        self.controlle_deque = controlle_deque

        self.register_ports()

        self.active = False

        # the level of each of the 8 tracks
        self.levels = np.ones(8, np.float64)

        # muted state
        self.muted = np.zeros(8, np.bool)

        # arrays representing data in the Launchpad Mini pads
        self.grid = np.zeros((8, 8), np.float64)
        self.column = np.zeros(8, np.float64)
        self.row = np.zeros(8, np.float64)
        self.row[4] = Color.FULL_GREEN.to_double()

    def register_ports(self):
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

    def process_audio(self, in_):
        """
        Mix incoming audio.

        """
        adjusted = in_ * self.levels * ~self.muted

        out = np.zeros((in_.shape[0], 2), np.float64)
        out[:, 0] = np.sum(adjusted[:, 0::2], 1)
        out[:, 1] = np.sum(adjusted[:, 1::2], 1)

        self.active = True  # XXX remove
        if not self.active:
            return

        amplitude = np.sqrt(2) * np.average(np.abs(adjusted), 0)
        power = np.log10(amplitude * 9 + 1)
        self.grid[:] = meter
        self.grid[power < meter] = 0
        self.column[:] = meter[:, 0]
        self.column[np.average(power, 0) < meter[:, 0]] = 0
        self.grid[7, :][self.muted] = Color.FULL_RED.to_double()
        arr = convert_to_color_array(self.grid, self.row, self.column)
        rapid_led_update(self.controlle_deque, arr)

        return out

    @process_event(Press(Grid))
    def adjust_level(self, pad):
        """
        Adjust the level for a track when a pad is pressed in the grid.

        If the bottom pad is pressed we toggle the mute state for the track.

        """
        if pad.y == 0:
            # toggle mute
            self.muted[pad.x] = ~self.muted[pad.x]
        else:
            level = np.linspace(0, 1, 8)[pad.y]
            self.levels[pad.x] = level

    @process_event(Press(Column))
    def adjust_levels(self, pad):
        """
        Adjust levels for all tracks.

        The bottom pad (H) toggles the mute state of all tracks.

        """
        if pad.y == 0:
            # toggle mute
            self.muted = ~self.muted
        else:
            level = np.linspace(0, 1, 8)[pad.y]
            self.levels[:] = level
