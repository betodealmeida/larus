from collections import defaultdict

import numpy as np


class Mode:

    audio_callbacks = {}
    midi_callbacks = defaultdict(dict)

    def __init__(self, client):
        self.client = client
        self.register_ports()

    def register_ports(self):
        raise NotImplementedError('Subclasses must implement register_ports')

    def process(self, frames):
        """
        Method called by the client for each event.

        """
        class_name = self.__class__.__name__

        if class_name in self.audio_callbacks:
            in_ = np.zeros((frames, len(self.inports)), np.float64)
            for i, port in enumerate(self.inports):
                in_[:, i] = port.get_array()

            out = np.zeros((frames, len(self.outports)), np.float64)
            func = self.audio_callbacks[class_name]
            func(in_, out)

            for i, port in enumerate(self.outports):
                port.get_array()[:] = out[:, i]

        for condition, func in self.midi_callbacks[class_name].items():
            for offset, indata in inport.incoming_midi_events():
                if condition(indata):
                    button = get_button(indata)
                    func(button)

    @classmethod
    def process_audio(cls, func):
        class_name = func.__qualname__.split('.')[0]
        cls.audio_callbacks[class_name] = func
        return func

    @classmethod
    def process_midi(cls, condition):
        def decorator(func):
            class_name = func.__qualname__.split('.')[0]
            cls.midi_callbacks[class_name][condition] = func
            return func
        return decorator
