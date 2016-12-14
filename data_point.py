class DataPoint:
    """
    Data point from a single sensor
    """

    def __init__(self, x=0.0, y=0.0, z=0.0, time=0.0, sensor_type=''):
        self.x = x
        self.y = y
        self.z = z
        self.time = time
        self.sensor_type = sensor_type

    def __str__(self):
        decimals = int(((self.time - int(self.time)) * 10000)) / 10000.0
        time_str = str(int(self.time) + decimals)
        return self.sensor_type + ',' + str(self.x) + ',' + str(self.y) + ',' + str(
            self.z) + ',' + time_str

    @staticmethod
    def from_str(serialized):
        comps = serialized.split(',')
        if len(comps) != 5:
            return None
        x = float(comps[1])
        y = float(comps[2])
        z = float(comps[3])
        time = float(comps[4])
        sensor_type = comps[0]
        return DataPoint(x, y, z, time, sensor_type)
