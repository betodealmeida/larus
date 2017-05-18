# -*- coding: utf-8 -*-

from collections import deque
import threading

import jack
import numpy as np

from config import CLIENT_NAME, MAX_NUMBER_OF_EVENTS
from modes.mixer import Mixer


class App:

    def __init__(self, client):
        self.client = client

        # create an event to wait for until shutdown
        self.event = threading.Event()

        # create a deque to store MIDI data that updates the controller
        self.controller_queue = deque(maxlen=MAX_NUMBER_OF_EVENTS)

        # initialize all modes
        self.modes = [
            Mixer(client, self.controller_queue),
        ]

        # register MIDI ports to talk to the controller
        self.to_controller = client.midi_outports.register('controller_output')
        self.from_controller = client.midi_inports.register('controller_input')

    def process(self, frames):
        # read from controller
        for offset, midi_event in self.from_controller.incoming_midi_events():
            # TODO: check if we need to activate any modes and pass relevant
            # events to them
            print(offset, midi_event)

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
        while self.controller_queue:
            midi_event = self.controller_queue.pop()
            self.to_controller.write_midi_event(midi_event)

    def shutdown(self, status, reason):
        print('JACK shutdown!')
        print('status:', status)
        print('reason:', reason)
        self.event.set()


def main():
    client = jack.client(CLIENT_NAME)
    app = App(client)

    client.set_process_callback(app.process)
    client.set_shutdown_callback(app.shutdown)

    client.activate()

    # connect app to controller
    controller_input = client.get_ports('.*Launchpad Mini.*\(playback\).*')
    controller_output = client.get_ports('.*Launchpad Mini.*\(capture\).*')
    client.connect(app.to_controller, controller_input)
    client.connect(app.from_controller, controller_output)

    with client:
        print('Press Ctrl+C to stop')
        try:
            app.event.wait()
        except KeyboardInterrupt:
            print('\nInterrupted by user')


if __name__ == '__main__':
    main()
