# -*- coding: utf-8 -*-

"""
# Larus mixer #

This is a 8-track mixer that displays levels in the Launchpad Mini, and whose
individual levels can be controlled from there.

"""

import numpy as np

import jack

from launchpad import BUTTON


class Mixer:

    select = BUTTON(5)

    def __init__(self, client: jack.Client) -> None:
        self.client = client
        self.register_ports()
        self.buffer = np.zeros((8, 8), 'f')

    def register_ports(self) -> None:
        """
        Register 8 input tracks and 2 output tracks.

        """
        self.inports = [
            self.client.inports.register(
                'input_{track}_{channel}'.format(
                    track=track, channel=channel))
            for track in (1, 2, 3, 4)
            for channel in (1, 2)
        ]
        self.outports = [
            self.client.outports.register('output_{channel}'.format(
                channel=channel))
            for channel in (1, 2)
        ]

    def process(self, frames) -> None:
        pass
