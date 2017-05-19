"""
Temporary module for testing drawing on the Launchpad.

"""

from collections import deque
from enum import Enum
import time

import jack
import numpy as np

RAPID_LED_UPDATE = 0x92
SET_GRID_LED = 0x90


class Color(Enum):
    OFF = 12
    LOW_RED = 13
    FULL_RED = 15
    LOW_AMBER = 29
    FULL_AMBER = 63
    FULL_YELLOW = 62
    LOW_GREEN = 28
    FULL_GREEN = 60

    def to_double(self):
        idx = palette.index(self)
        return np.linspace(0, 1, 9)[1:][idx]


palette = [
    Color.LOW_GREEN,
    Color.FULL_GREEN,
    Color.FULL_YELLOW,
    Color.LOW_AMBER,
    Color.FULL_AMBER,
    Color.LOW_RED,
    Color.FULL_RED,
]


def rapid_led_update(deque, arr):
    """
    Address all 80 LEDs with 40 consecutive instructions.

    The array `arr` should be an (10, 8) array of colors as integers.

    """
    for v1, v2 in arr.reshape(-1, 2):
        deque.appendleft((0, (RAPID_LED_UPDATE, v1, v2)))

    # exit rapid LED update mode by resending a value with regular status
    deque.appendleft((0, (SET_GRID_LED, 0x0, arr[0, 0])))


def convert_to_color_array(grid, row, column):
    in_ = np.vstack([grid, column, row])
    out = np.ones((10, 8), np.int32) * Color.OFF.value

    # convert from 0-1 to color
    thresholds = np.linspace(0, 1, 9)
    for threshold, color in zip(thresholds, palette):
        out[in_ > threshold] = color.value

    return out


client = jack.Client('Larus')
outport = client.midi_outports.register('output')
q = deque(maxlen=100)


@client.set_process_callback
def process(frames):
    outport.clear_buffer()

    offset = 0
    print(len(q))
    while q:
        event = q.pop()
        outport.write_midi_event(offset, event)
        offset += 1


def main():
    client.activate()
    client.connect(
        outport, 'a2j:Launchpad Mini [20] (playback): Launchpad Mini MIDI 1')

    # reset
    q.appendleft((0, (0xb0, 0, 0)))

    t = 0
    while True:
        grid = np.ones((8, 8)) * np.sin(np.pi / 2 * np.arange(t, t + 8)/8)
        grid = (grid + 1) / 2
        draw_array(q, grid)
        time.sleep(0.01)
        t += 1


if __name__ == '__main__':
    main()
