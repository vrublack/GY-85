"""
PYTHON driver for the ADXL-345 (3 axes accelerometer from Analog Device)
This driver use the 4-wire SPI protocol to communicate (see README)
"""

import spidev
import adxl345.base

WRITE_MASK = 0x0
READ_MASK = 0x80
MULTIREAD_MASK = 0x40

class ADXL345(adxl345.base.ADXL345_Base):

  def __init__(self, spi_bus=0, spi_device=0):
    self.spi = spidev.SpiDev()
    self.spi.open(spi_bus, spi_device)
    self.spi.mode = 0b11
    self.spi.max_speed_hz = 5000000
    self.spi.bits_per_word = 8
    self.spi.threewire = False
    self.spi.cshigh = False
    self.spi.lsbfirst = False

  def get_register(self, address):
    value = self.spi.xfer2( [ (address & 0x3F) | READ_MASK ] )
    return value;

  def get_registers(self, address, count):
    self.spi.writebytes( [ address & 0x3F ] | READ_MASK | MULTIREAD_MASK )
    value = self.spi.readbytes(count)
    return value

  def set_register(self, address, value):
    self.spi.writebytes( [ address, value ] )

