#!/usr/bin/env python3

"""Simple example with numpy arrays."""
import Adafruit_ADS1x15
import multiprocessing
import numpy
import numpy.matlib
import ringbuffer


most_recent = 0.0

def writer(ring):
    adc = Adafruit_ADS1x15.ADS1015()
    GAIN = 8
    adc.start_adc(0,gain=GAIN) # start continous sampling on pin 0

    for i in range(10):
        most_recent = adc.get_last_result()
        x = numpy.array(adc.get_last_result(), dtype=float)
        try:
            ring.try_write(numpy.ctypeslib.as_ctypes(x))
        except ringbuffer.WaitingForReaderError:
            print('Reader is too slow, dropping %r' % x)
            continue

        if i and i % 100 == 0:
            print('Wrote %d so far' % i)

    ring.writer_done()
    print('Writer is done')


def reader(ring, pointer):
    while True:
        try:
            data = ring.blocking_read(pointer)
        except ringbuffer.WriterFinishedError:
            return
        # print(data)
        # x = numpy.frombuffer(data)
        # print(x)
        print(most_recent)


    print('Reader %r is done' % pointer)


def main():
    # size of an entry (8 bytes per float), size of the circular buffer
    ring = ringbuffer.RingBuffer(slot_bytes=8, slot_count=50)
    ring.new_writer()

    processes = [
        multiprocessing.Process(target=writer, args=(ring,)),
    ]
    for i in range(10):
        processes.append(multiprocessing.Process(
            target=reader, args=(ring, ring.new_reader())))

    for p in processes:
        p.start()

    for p in processes:
        p.join(timeout=20)
        assert not p.is_alive()
        assert p.exitcode == 0


if __name__ == '__main__':
    main()