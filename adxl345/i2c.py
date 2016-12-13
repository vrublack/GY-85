"""
PYTHON driver for the ADXL-345 (3 axes accelerometer from Analog Device)
This driver use the I2C protocol to communicate (see README)
"""

import smbus
import adxl345.base

class ADXL345(adxl345.base.ADXL345_Base):

  STD_ADDRESS = 0x1D
  ALT_ADDRESS = 0x53

  def __init__(self, alternate=False, port=1):
    """ Initialize the driver
    :param alternate: use the standard or alternate I2C address as selected by pin SDO/ALT_ADDRESS
    :param port: number of I2C bus to use
    """
    self.bus = smbus.SMBus(port)
    if alternate: 
      self.i2caddress = ADXL345.ALT_ADDRESS
    else:
      self.i2caddress = ADXL345.STD_ADDRESS

  def get_register(self, address):
    bytes = self.bus.read_i2c_block_data(self.i2caddress, address, 1)
    return bytes[0]

  def get_registers(self, address, count):
    bytes = self.bus.read_i2c_block_data(self.i2caddress, address, count)
    return bytes

  def set_register(self, address, value):
    self.bus.write_byte_data(self.i2caddress, address, value)

