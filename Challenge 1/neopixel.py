from neopixel import NeoPixel
import pyb
from pyb import Pin

# create neopixel object
np = NeoPixel(Pin("Y12", Pin.OUT), 8)
for i in range(8):  # all LEDs dark
    np[i] = (0, 0, 0)
    np.write()
    pyb.delay(1)

for i in range(8):  # turn LEDs red one at a time
    np[i] = (64, 0, 0)
    np.write()
    pyb.delay(300)

for i in range(8):  # turn LEDs blue one at a time
    np[i] = (0, 0, 64)
    np.write()
    pyb.delay(300)

for i in range(8):  # turn all LEDs off
    np[i] = (0, 0, 0)
    np.write()
    pyb.delay(1)