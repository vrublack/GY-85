class SensorPrinter:
    """
    Simply prints samples that it receives
    """
    def on_sensor_data_changed(self, reading):
        print(str(reading))

        return True
