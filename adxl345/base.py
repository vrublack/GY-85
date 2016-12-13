"""
PYTHON base driver for the ADXL-345 (3 axes accelerometer from Analog Device)
This driver class is abstract and a concrete implementation (either I2C or SPI) should be used

This abstract class holds all methods that you should be able to call on client side.
Concrete subclasses only implement the communication protocol between the master host (the one running python) and the ADXL device
"""

from __future__ import division
import math


class ADXL345_Base:
    # Registers
    REG_DEVICE_ID = 0x00
    REG_THRESH_TAP = 0x1D
    REG_OFSX = 0x1E
    REG_OFSY = 0x1F
    REG_OFSZ = 0x20
    REG_DUR = 0x21
    REG_LATENT = 0x22
    REG_WINDOW = 0x23
    REG_THRESH_ACT = 0x24
    REG_THRESH_INACT = 0x25
    REG_TIME_INACT = 0x26
    REG_ACT_INACT_CTL = 0x27
    REG_THRESH_FF = 0x28
    REG_TIME_FF = 0x29
    REG_TAP_AXES = 0x2A
    REG_ACT_TAP_STATUS = 0x2B
    REG_BW_RATE = 0x2C
    REG_POWER_CTL = 0x2D
    REG_INT_ENABLE = 0x2E
    REG_INT_MAP = 0x2F
    REG_INT_SOURCE = 0x30
    REG_DATA_FORMAT = 0x31
    REG_DATAX0 = 0x32
    REG_DATAX1 = 0x33
    REG_DATAY0 = 0x34
    REG_DATAY1 = 0x35
    REG_DATAZ0 = 0x36
    REG_DATAZ1 = 0x37
    REG_FIFO_CTL = 0x38
    REG_FIFO_STATUS = 0x39

    # Full Resolution scale factor (0x100 LSB/g ~= 3.9/1000 mg/LSB)
    SCALE_FACTOR = 1 / 0x100

    def __init__(self):
        self._full_resolution = True
        self._range = 0

    def get_register(self, address):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_registers(self, address, count):
        raise NotImplementedError("This method should be implemented by subclasses")

    def set_register(self, address, value):
        raise NotImplementedError("This method should be implemented by subclasses")

    def get_device_id(self):
        return self.get_register(ADXL345_Base.REG_DEVICE_ID)

    def set_data_rate(self, hz, low_power=False):
        if hz >= 3200:
            rate = 3200
            rate_code = 0b1111
        elif hz >= 1600 and hz < 3200:
            rate = 1600
            rate_code = 0b1110
        elif hz >= 800 and hz < 1600:
            rate = 800
            rate_code = 0b1101
        elif hz >= 400 and hz < 800:
            rate = 400
            rate_code = 0b1100
        elif hz >= 200 and hz < 400:
            rate = 200
            rate_code = 0b1011
        elif hz >= 100 and hz < 200:
            rate = 100
            rate_code = 0b1010
        elif hz >= 50 and hz < 100:
            rate = 50
            rate_code = 0b1001
        elif hz >= 25 and hz < 50:
            rate = 25
            rate_code = 0b1000
        elif hz >= 25 / 2 and hz < 25:
            rate = 25 / 2
            rate_code = 0b0111
        elif hz >= 25 / 4 and hz < 25 / 2:
            rate = 25 / 4
            rate_code = 0b0110
        elif hz >= 25 / 8 and hz < 25 / 4:
            rate = 25 / 8
            rate_code = 0b0101
        elif hz >= 25 / 16 and hz < 25 / 8:
            rate = 25 / 16
            rate_code = 0b0100
        elif hz >= 25 / 32 and hz < 25 / 16:
            rate = 25 / 32
            rate_code = 0b0011
        elif hz >= 25 / 64 and hz < 25 / 32:
            rate = 25 / 64
            rate_code = 0b0010
        elif hz >= 25 / 128 and hz < 25 / 64:
            rate = 25 / 128
            rate_code = 0b0001
        elif hz < 25 / 128:
            rate = 25 / 256
            rate_code = 0

        if low_power:
            rate_code = rate_code | 0x10

        self.set_register(ADXL345_Base.REG_BW_RATE, rate_code)
        return rate

    def _equal(self, value, reference, error_margin=0.1):
        return value >= (reference - error_margin) and value <= (reference + error_margin)

    def _convert(self, lsb, msb):
        """ Convert the gravity data returned by the ADXL to meaningful values """
        value = lsb | (msb << 8)
        if value & 0x8000:
            value = -value ^ 0xFFFF
        if not self._full_resolution:
            value = value << self._range
        value *= ADXL345_Base.SCALE_FACTOR
        return value

    def _set_power_ctl(self, measure, wake_up=0, sleep=0, auto_sleep=0, link=0):
        power_ctl = wake_up & 0x03

        if sleep:
            power_ctl |= 0x04
        if measure:
            power_ctl |= 0x08
        if auto_sleep:
            power_ctl |= 0x10
        if link:
            power_ctl |= 0x20

        self.set_register(ADXL345_Base.REG_POWER_CTL, power_ctl)

    def _send_data_format(self, self_test=0, spi=0, int_invert=0, justify=0):
        data_format = self._range & 0x03

        if justify:
            data_format |= 0x04
        if self._full_resolution:
            data_format |= 0x08
        if int_invert:
            data_format |= 0x20
        if spi:
            data_format |= 0x40
        if self_test:
            data_format |= 0x80

        self.set_register(ADXL345_Base.REG_DATA_FORMAT, data_format)

    def _set_fifo_mode(self, mode=0, trigger=0, samples=0x1F):
        fifo_ctl = samples & 0x1F
        fifo_ctl = fifo_ctl | ((mode & 0x03) << 6)

        if trigger:
            fifo_ctl |= 0x20

        self.set_register(ADXL345_Base.REG_FIFO_CTL, fifo_ctl)

    def power_on(self):
        self._set_power_ctl(True)

    def power_off(self):
        self._set_power_ctl(False)

    def set_range(self, range, full_resolution=True):
        """ Set the G range and the resolution. Valid range values are 2, 4, 8, 16. Full resolution set either 10-bit or 13-bit resolution """
        if range == 2:
            range_code = 0x0
        elif range == 4:
            range_code = 0x1
        elif range == 8:
            range_code = 0x2
        elif range == 16:
            range_code = 0x3
        else:
            raise ValueError("invalid range [" + str(range) + "] expected one of [2, 4, 8, 16]")

        self._range = range_code
        self._full_resolution = full_resolution
        self._send_data_format()

    def read_data(self):
        """ return values for the 3 axes of the ADXL, expressed in g (multiple of earth gravity) """
        bytes = self.get_registers(ADXL345_Base.REG_DATAX0, 6)
        x = self._convert(bytes[0], bytes[1])
        y = self._convert(bytes[2], bytes[3])
        z = self._convert(bytes[4], bytes[5])
        return (x, y, z)

    def get_fifo_count(self):
        count = self.get_register(ADXL345_Base.REG_FIFO_STATUS)
        return count & 0x7F

    def get_fifo(self):
        """ return an array of the whole FIFO """
        fifo_count = self.get_fifo_count()
        fifo = []
        for num in range(0, fifo_count):
            fifo.append(self.read_data())
        return fifo

    def enable_fifo(self, stream=True):
        if stream:
            self._set_fifo_mode(mode=0x02)
        else:
            self._set_fifo_mode(mode=0x01)

    def disable_fifo(self):
        self._set_fifo_mode(mode=0x00)

    def set_offset(self, x, y, z):
        """ set hardware offset for the 3 axes of the ADXL, units are g """

        def convert_offet(value):
            value = value / ADXL345_Base.SCALE_FACTOR / 4
            bytes = int(value) & 0xFF
            return bytes

        self.set_register(ADXL345_Base.REG_OFSX, convert_offet(x))
        self.set_register(ADXL345_Base.REG_OFSY, convert_offet(y))
        self.set_register(ADXL345_Base.REG_OFSZ, convert_offet(z))

    def calibrate(self):
        """ Auto calibrate the device offset. Put the device so as one axe is parallel to the gravity field (usually, put the device on a flat surface) """
        self.set_offset(0, 0, 0)
        samples = self.read_data()

        x = samples['x']
        y = samples['y']
        z = samples['z']

        abs_x = math.fabs(x)
        abs_y = math.fabs(y)
        abs_z = math.fabs(z)

        # Find which axe is in the field of gravity and set its expected value to 1g absolute value
        if self._equal(abs_x, 1) and self._equal(abs_y, 0) and self._equal(abs_z, 0):
            cal_x = 1 if x > 0 else -1
            cal_y = 0
            cal_z = 0
        elif self._equal(abs_x, 0) and self._equal(abs_y, 1) and self._equal(abs_z, 0):
            cal_x = 0
            cal_y = 1 if y > 0 else -1
            cal_z = 0
        elif self._equal(abs_x, 0) and self._equal(abs_y, 0) and self._equal(abs_z, 1):
            cal_x = 0
            cal_y = 0
            cal_z = 1 if z > 0 else -1
        else:
            raise ValueError("Could not determine ADXL position. One axe should be set in field of gravity")

        offset_x = cal_x - x
        offset_y = cal_y - y
        offset_z = cal_z - z

        self.set_offset(offset_x, offset_y, offset_z)

        return {'x': offset_x,
                'y': offset_y,
                'z': offset_z}
