from sensor_listener import SensorListener
from sensor_reader import SensorReader

sensor_reader = SensorReader()
sensor_reader.set_sensor_listener(SensorListener())

sensor_reader.start_reading()
