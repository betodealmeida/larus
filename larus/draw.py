"""
Temporary module for testing drawing on the Launchpad.

"""

from enum import Enum
import queue
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


def rapid_led_update(q, grid, row, column):
    """
    Address all 80 LEDs with 40 consecutive instructions.

    """
    # grid
    for v1, v2 in grid.reshape(-1, 2):
        q.put((RAPID_LED_UPDATE, v1, v2))

    # column, from A to H
    for v1, v2 in column.reshape(-1, 2):
        q.put((RAPID_LED_UPDATE, v1, v2))

    # row, from 1 to 8
    for v1, v2 in row.reshape(-1, 2):
        q.put((RAPID_LED_UPDATE, v1, v2))

    # exit rapid LED update mode by resending a value with regular status
    q.put((SET_GRID_LED, 0x70, grid[0, 0]))


def draw_array(q, arr):
    row = np.ones(8, np.int32) * Color.OFF.value
    column = np.ones(8, np.int32) * Color.OFF.value
    grid = np.ones((8, 8), np.int32) * Color.OFF.value

    # convert from 0-1 to color
    palette = [
        Color.LOW_GREEN,
        Color.FULL_GREEN,
        Color.FULL_YELLOW,
        Color.LOW_AMBER,
        Color.FULL_AMBER,
        Color.LOW_RED,
        Color.FULL_RED,
    ]
    thresholds = np.linspace(0, 1, 9)
    for threshold, color in zip(thresholds, palette):
        grid[arr > threshold] = color.value

    rapid_led_update(q, grid, row, column)


client = jack.Client('Larus')
outport = client.midi_outports.register('output')
q = q = queue.Queue()


@client.set_process_callback
def process(frames):
    outport.clear_buffer()

    offset = 0
    while not q.empty():
        event = q.get()
        outport.write_midi_event(offset, event)
        offset += 1


def main():
    client.activate()
    client.connect(
        outport, 'a2j:Launchpad Mini [20] (playback): Launchpad Mini MIDI 1')

    # reset
    q.put((0xb0, 0, 0))

    t = 0
    while True:
        grid = np.ones((8, 8)) * np.sin(np.pi / 2 * np.arange(t, t + 8)/8)
        grid = (grid + 1) / 2
        draw_array(q, grid)
        time.sleep(0.01)
        t += 1


if __name__ == '__main__':
    main()
