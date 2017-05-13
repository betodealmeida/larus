# -*- coding: utf-8 -*-

"""
# Larus mixer #

This is a 8-track mixer that displays levels in the Launchpad Mini, and whose
individual levels can be controlled from there.

"""

import numpy as np

import jack

from core import Mode
from launchpad import Button, Color, Grid


# create an array of colors where the bottom is LOW_GREEN and the top is
# FULL_RED, in order to display the levels of each track
palette = np.linspace(Color.LOW_GREEN, Color.FULL_RED, 8)
meter = np.ones((8, 8), np.float64) * palette.reshape(8, 1)


class Mixer(Mode):

    # the mixer mode is activated by pressing button #5 in the top row
    select = Button(5)

    def __init__(self, client: jack.Client) -> None:
        self.client = client
        self.register_ports()

        # the level of each of the 8 tracks; start at 66%
        self.levels = np.ones(8, np.float64) * 0.66

        # buffer representing data in the Launchpad Mini
        self.buffer = np.zeros((8, 8), np.float64)

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
        Mix incoming audio and update buffer.

        """
        adjusted = in_ * self.levels
        out[:, 0] = np.average(adjusted[:, 0::2], 1)
        out[:, 1] = np.average(adjusted[:, 1::2], 1)

        # TODO: dB = 20 * log10(amplitude)
        amplitude = np.average(out, 0)
        self.buffer = meter[:]
        self.buffer[amplitude < meter] = 0

    @Mode.process_midi(Grid)
    def adjust_level(self, button):
        """
        Adjust the level for a track when a button is pressed in the grid.

        """
        level = np.linspace(0, 1, 8)[button.y - 1]
        self.levels[button.x - 1] = level

    @Mode.process_midi(Column)
    def adjust_levels(self, button):
        """
        Adjust levels for all tracks.

        """
        level = np.linspace(0, 1, 8)[button.y - 1]
        self.levels[:] = level
