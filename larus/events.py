from collections import defaultdict


class EventManager:

    callbacks = defaultdict(dict)

    @classmethod
    def process_event(cls, event):
        def decorator(func):
            class_name = func.__qualname__.split('.')[0]
            cls.callbacks[class_name][event] = func
            return func
        return decorator


class Pad:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Event:

    def __init__(self, target):
        self.target = target
        self.trigger = None

    def match(self, midi_event):
        raise NotImplementedError('Subclasses must implement `match`')


class Press(Event):

    """
    Note on + note off event.

    """

    def __init__(self, target):
        super().__init__(target)

        # keep track if the button was pressed, so we can match the event when
        # it's relased
        self.pressed = False

    def match(self, midi_event):
        note_on, note_off = self.target.match(midi_event)
        self.trigger = self.get_trigger(midi_event)

        if note_on:
            self.pressed = True
        elif note_off and self.pressed:
            self.pressed = False
            return True

    def get_trigger(self, midi_event):
        # return single pad
        pitch = midi_event[1]
        x = pitch % 8
        y = 7 - (pitch // 16)
        return Pad(x, y)


class Target:

    note_on = []
    note_off = []

    @classmethod
    def match(cls, midi_event):
        return midi_event in cls.note_on, midi_event in cls.note_off


class Column(Target):

    note_on = [(144, pitch, 127) for pitch in range(8, 136, 16)]
    note_off = [(128, pitch, 64) for pitch in range(8, 136, 16)]


class Grid(Target):

    note_on = [(144, y * 16 + x, 127) for y in range(8) for x in range(8)]
    note_off = [(128, y * 16 + x, 64) for y in range(8) for x in range(8)]


process_event = EventManager.process_event
