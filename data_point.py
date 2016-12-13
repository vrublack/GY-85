class DataPoint:
    """
    Data point from a single sensor
    """

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.time = 0.0
        self.sensor_type = ''

    def __str__(self):
        return str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ' (' + self.sensor_type + ')'