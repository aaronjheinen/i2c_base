I2CBase
=======

This base block is to help write blocks that communicate with chips over I2C. It provides functionality so that your blocks work on a variety of platforms.

Properties
----------

-   **platform**: The Platform used for i2c communication (e.g. RaspberryPi|Edison|FT232H|...)
-   **I2C_address**: I2C address to communicate with (e.g. '0x40')

Dependencies
------------

Not all dependencies are required for all uses of the block. It matters what `Platform` you are using.

FT232H
-----------

Communicate I2C over USB with a [FT232H chip](http://www.adafruit.com/product/2264).

-   [**Adafruit_Python_GPIO**](https://github.com/neutralio/Adafruit_Python_GPIO/tree/htu-python3-v2)
-   [**libftdi**](https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup)


1. This block uses the Adafuit_Python_GPIO package for I2C communication but it requires a [special branch](https://github.com/neutralio/Adafruit_Python_GPIO/tree/htu-python3-v2) that supports python 3.

2. Also required is the libftdi library for communicating with the FT232H chip. Follow the Adafruit [install instructions](https://learn.adafruit.com/adafruit-ft232h-breakout/linux-setup) with two slight modifications.

    1. Replace the step `cmake -DCMAKE_INSTALL_PREFIX="/usr/" ../` with  `cmake -DCMAKE_INSTALL_PREFIX="/usr/" -DPYTHON_EXECUTABLE="/usr/bin/python3.4" ../`.
    2. After the `cmake ...` step and before the `make` step. Modify the file `build/python/ftdi1PYTHON_wrap.c`. In line 3161, replace `PyUnicode_AsUTF8String` with `PyUnicode_AsLatin1String`. Otherwise the library won't work completely with python3. A bug has reported to the libftdi [mailing list](http://developer.intra2net.com/mailarchive/html/libftdi/2015/msg00100.html).


Commands
--------
None

Input
-----
Any list of signals.

Output
------
None
