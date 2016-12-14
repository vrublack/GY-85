import os
from os import listdir
from os.path import isfile, join
import multiprocessing
from multiprocessing import Queue

stop = multiprocessing.Value("i", 0)

class StdoutWriter:
    """
    Like FileWriter but prints to stdout instead of a file
    """
    def __init__(self, nth_sample=1):
        """

        :param nth_sample: Only every nth sample is printed. Use 1 to print every single sample.
        """

        # for multiprocessing
        self.__buffer = Queue()
        self.nth_sample = nth_sample

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

        print(str(sample))

    def start_write_loop(self):
        """
        Starts consumer loop that writes data points to a file. Runs on consumer process.
        """

        global stop
        stop.value = 0

        count = 0

        while True:
            # This obviously is a very naive implementation of the consumer (while loop instead of lock).
            # However, this already achieves the maximum sampling rate because the I2C communication with
            # the sensors is the bottleneck.
            if not self.__buffer.empty():
                data_point = self.__buffer.get()
                if count % self.nth_sample == 0:
                    self._write_sample(data_point)
                count += 1