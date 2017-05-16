# -*- coding: utf-8 -*-

import threading

import jack
import numpy as np

from mixer import Mixer


client = jack.Client("Larus")
event = threading.Event()


@client.set_process_callback
def process(frames):
    assert frames == client.blocksize
    for i, _o in zip(client.inports, client.outports):
        print(np.average(i.get_array()))
        # o.get_buffer()[:] = i.get_buffer()


@client.set_shutdown_callback
def shutdown(status, reason):
    print('JACK shutdown!')
    print('status:', status)
    print('reason:', reason)
    event.set()


def main():
    Mixer(client)
    client.activate()

    with client:
        print('Press Ctrl+C to stop')
        try:
            event.wait()
        except KeyboardInterrupt:
            print('\nInterrupted by user')


if __name__ == '__main__':
    main()
