from multiprocessing import Process

import sys
import argparse
import file_writer
import stdout_writer
from stdout_writer import StdoutWriter
from sensor_reader import SensorReader
from file_writer import FileWriter


parser = argparse.ArgumentParser()
parser.add_argument("--stdout", help="write to stdout instead of file", action="store_true")
parser.add_argument("-nth", type=int, help="only print ever nth sample if --stdout is specified")
args = parser.parse_args()


sensor_reader = SensorReader()
if args.stdout:
    if args.nth is not None:
        writer = StdoutWriter(args.nth)
    else:
        writer = StdoutWriter()
else:
    writer = FileWriter('/home/pi/sensor_recordings/')
sensor_reader.set_sensor_listener(writer)

while True:

    # Consumer/producer architecture: the SensorReader is the producer, reading data from sensors,
    # and the FileWriter is the consumer.
    # We use multiprocessing.Process instead of threading.Thread because the latter would also cause
    # the other thread to slow down due to Global Interpreter Lock.

    # reset this because sensor_reader.start_reading() might execute before file_writer.start_write_loop()
    if args.stdout:
        stdout_writer.stop.value = 0
    else:
        file_writer.stop.value = 0
    process = Process(target=writer.start_write_loop)
    process.start()

    sensor_reader.start_reading()
