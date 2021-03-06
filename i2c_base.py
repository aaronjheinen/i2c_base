from enum import Enum
import logging
from nio.block.base import Block
from nio.properties import SelectProperty, StringProperty
import tenacity

class I2CDevice():

    def __init__(self, address):
        self._address = address

    def write_list(self, register, data):
        """ Write a list of bytes """
        raise NotImplemented()

    def read_bytes(self, length):
        """ Read a length number of bytes (without register). Results are
        returned as a bytearray """
        raise NotImplemented()

class Generic_I2CDevice(I2CDevice):
    def __init__(self, address, bus):
        super().__init__(address)
        self._bus = "/dev/i2c-" + bus
        self._msg = []

    def write_list(self, register, data):
        # HTU block is written badly, so this is the work around for now
        #  stored register to write to and then call read to read
        from periphery import I2C
        if isinstance(register, int):
            register = register.to_bytes(1, 'big')
        self._msg = [I2C.Message(register)]

    @tenacity.retry(stop=tenacity.stop_after_attempt(12),
        retry=tenacity.retry_if_exception_type(tenacity.TryAgain),
         wait=tenacity.wait_fixed(0.5))
    def read_bytes(self, length):
        #returns list of length 'length'
        from periphery import I2C, I2CError
        i2c = I2C(self._bus)
        self._msg.append(I2C.Message([0x00]*length, read=True))
        try:
            i2c.transfer(self._address, self._msg)
        except I2CError as err:
            self._msg.pop()
            raise tenacity.TryAgain
        i2c.close()
        return_data = self._msg[-1].data
        self._msg=[]
        return return_data

class RaspberryPi_I2CDevice(I2CDevice):

    def __init__(self, address):
        super().__init__(address)
        import io
        import fcntl
        bus = 1
        self._read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self._write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)
        # set device address
        fcntl.ioctl(self._read, 0x0703, address)
        fcntl.ioctl(self._write, 0x0703, address)

    def write_list(self, register, data):
        # TODO: figure out how to actually write the data, this has only been
        # tested with the HTU21d block.
        if isinstance(register, int):
            return self._write.write(register.to_bytes(1, 'big'))
        else:
            return self._write.write(register)

    def read_bytes(self, length):
        return self._read.read(length)


class FT232H_I2CDevice(I2CDevice):

    def __init__(self, address):
        super().__init__(address)
        import Adafruit_GPIO.FT232H as FT232H
        # Temporarily disable FTDI serial drivers.
        FT232H.use_FT232H()
        # Find the first FT232H device.
        ft232h = FT232H.FT232H()
        # Get the I2C device for the configured address
        self._device = FT232H.I2CDevice(ft232h, address)

    def write_list(self, register, data):
        return self._device.writeList(register, data)

    def read_bytes(self, length):
        return self._device.readBytes(length)


class Platform(Enum):
    raspberry_pi = 0
    ft232h = 1
    generic = 2


class I2CBase(Block):

    """ Communicate I2C using the selected Platform """

    platform = SelectProperty(Platform,
                              title='Platform',
                              default=Platform.generic)
    address = StringProperty(title='I2C Address', default="0x00")
    bus = StringProperty(title='Bus', default='1')

    def __init__(self):
        super().__init__()
        self._i2c = None

    def configure(self, context):
        super().configure(context)
        address = int(self.address(), 0)
        self.logger.debug(
            "Creating device adaptor: {}, address: {}".format(
                self.platform().name, address))
        if self.platform().value == Platform.raspberry_pi.value:
            self._i2c = RaspberryPi_I2CDevice(address)
        elif self.platform().value == Platform.ft232h.value:
            logging.getLogger('Adafruit_GPIO.FT232H').setLevel(
                self.logger.logger.level)
            self._i2c = FT232H_I2CDevice(address)
        elif self.platform().value == Platform.generic.value:
            self._i2c = Generic_I2CDevice(address, self.bus())
        else:
            self.logger.warning("Warning! Unknown device adaptor type.")
            self._i2c = I2CDevice(address)
        self.logger.debug("Created device adaptor")
