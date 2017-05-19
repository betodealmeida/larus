# -*- coding: utf-8 -*-

from collections import deque
import struct
import threading

import jack
import numpy as np

from config import CLIENT_NAME, MAX_NUMBER_OF_EVENTS
from events import EventManager
from modes.mixer import Mixer


class App:

    def __init__(self, client):
        self.client = client

        # create an event to wait for until shutdown
        self.event = threading.Event()

        # create a deque to store MIDI data that updates the controller
        self.controlle_deque = deque(maxlen=MAX_NUMBER_OF_EVENTS)

        # initialize all modes
        self.modes = [
            Mixer(client, self.controlle_deque),
        ]

        # register MIDI ports to talk to the controller
        self.to_controller = client.midi_outports.register('controller_output')
        self.from_controller = client.midi_inports.register('controller_input')

    def process(self, frames):
        # read from controller
        for _offset, midi_event in self.from_controller.incoming_midi_events():
            midi_event = struct.unpack('3B', midi_event)
            for mode in self.modes:
                # activate? XXX
                # process event?
                if mode.active:
                    self.process_callbacks(mode, midi_event)

        # process audio
        for mode in self.modes:
            in_ = np.zeros((frames, len(mode.inports)), np.float64)
            for i, port in enumerate(mode.inports):
                in_[:, i] = port.get_array()
            out = mode.process_audio(in_)
            for i, port in enumerate(mode.outports):
                port.get_array()[:] = out[:, i]

        # send data to the controller
        self.to_controller.clear_buffer()
        while self.controlle_deque:
            offset, midi_event = self.controlle_deque.pop()
            self.to_controller.write_midi_event(offset, midi_event)

    def process_callbacks(self, mode, midi_event):
        class_name = mode.__class__.__name__
        for event, callback in EventManager.callbacks[class_name].items():
            if event.match(midi_event):
                callback(mode, event.trigger)

    def shutdown(self, status, reason):
        print('JACK shutdown!')
        print('status:', status)
        print('reason:', reason)
        self.event.set()


def main():
    client = jack.Client(CLIENT_NAME)
    app = App(client)

    client.set_process_callback(app.process)
    client.set_shutdown_callback(app.shutdown)
    client.activate()

    # connect app to controller
    client.connect(
        app.to_controller,
        'a2j:Launchpad Mini [20] (playback): Launchpad Mini MIDI 1',
    )
    client.connect(
        'a2j:Launchpad Mini [20] (capture): Launchpad Mini MIDI 1',
        app.from_controller,
    )

    with client:
        print('Press Ctrl+C to stop')
        try:
            app.event.wait()
        except KeyboardInterrupt:
            print('\nInterrupted by user')


if __name__ == '__main__':
    main()
