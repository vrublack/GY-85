import os
from os import listdir
from os.path import isfile, join
import multiprocessing
from multiprocessing import Queue

stop = multiprocessing.Value("i", 0)


class FileWriter:
    def __init__(self, path='/home/pi/sensor_recordings/'):
        """

        :param path: Directory in which files will be written
        """

        # for multiprocessing
        self.__buffer = Queue()
        self.path = path
        self.fname = None

    def _write_header(self):
        self.__f.write("Sensor type,x,y,z,time (ms)\n")

    def on_sensor_data_changed(self, data_point):
        """
        Passes data to the consumer (consumer/producer architecture). Runs on producer process.
        :returns If the writer has been stopped
        """

        global stop

        if stop.value != 0:
            return False
        else:
            self.__buffer.put(data_point)
            return True

    def _write_sample(self, sample):
        """
        :param sample: Writes a DataPoint to the file
        :return:
        """

        if self.fname is None:
            self._new_file()

        self.written += 1
        self.__f.write(str(sample) + '\n')

    def start_write_loop(self):
        """
        Starts consumer loop that writes data points to a file. Runs on consumer process.
        """

        global stop
        stop.value = 0

        while True:
            # This obviously is a very naive implementation of the consumer (while loop instead of lock).
            # However, this already achieves the maximum sampling rate because the I2C communication with
            # the sensors is the bottleneck.
            if not self.__buffer.empty():
                data_point = self.__buffer.get()
                self._write_sample(data_point)

    def file_size(self):
        """

        :return: Size of file in MB
        """
        return os.stat(join(self.path, self.fname)).st_size / 1000.0

    def _new_file(self):
        # Files are named 'recording_x' where x is a sequence number. Find the highest sequence number in the dir and add 1.
        files_in_dir = [f for f in listdir(self.path) if isfile(join(self.path, f))]
        max_number = 0
        for f in files_in_dir:
            if f.startswith('recording_'):
                number = int(f[10:])
                if number > max_number:
                    max_number = number
        filename = 'recording_' + str(max_number + 1)
        self.__f = open(join(self.path, filename), 'w')
        self._write_header()
        self.fname = filename
        self.written = 0

        print('Writing to file ' + join(self.path, filename))
