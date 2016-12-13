from multiprocessing import Process

import file_writer
from sensor_reader import SensorReader
from file_writer import FileWriter

sensor_reader = SensorReader()
writer = FileWriter('/home/pi/sensor_recordings/')
sensor_reader.set_sensor_listener(writer)

while True:

    # Consumer/producer architecture: the SensorReader is the producer, reading data from sensors,
    # and the FileWriter is the consumer.
    # We use multiprocessing.Process instead of threading.Thread because the latter would also cause
    # the other thread to slow down due to Global Interpreter Lock.

    # reset this because sensor_reader.start_reading() might execute before file_writer.start_write_loop()
    file_writer.stop.value = 0
    process = Process(target=writer.start_write_loop)
    process.start()

    sensor_reader.start_reading()
