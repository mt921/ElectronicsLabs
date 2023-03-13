import pyb
from pyb import LED
from oled_938 import OLED_938
from mpu6050 import MPU6050

# Define LEDs
b_LED = LED(4)

# I2C connected to Y9, Y10 (I2C bus 2) and Y11 is reset low active
i2c = pyb.I2C(2, pyb.I2C.MASTER)
devid = i2c.scan()				# find the I2C device number
oled = OLED_938(
    pinout={"sda": "Y10", "scl": "Y9", "res": "Y8"},
    height=64, external_vcc=False, i2c_devid=i2c.scan()[0],
)
oled.poweron()
oled.init_display()

# IMU connected to X9 and X10
imu = MPU6050(1, False)    	# Use I2C port 1 on Pyboard

def read_imu(dt):
	
	global g_pitch
	alpha = 0.7    # larger = longer time constant
	pitch = int(imu.pitch())
	roll = int(imu.roll())
	# show graphics
	oled.clear()
	oled.draw_text(0,15,'Pitch Angle:{:5d}'.format(pitch))
	oled.draw_text(0,30,'Roll Angle{:5d}'.format(roll))
	oled.display()
		
tic = pyb.millis()		
while True:
	b_LED.toggle()
	toc = pyb.millis()
	read_imu(toc-tic)
	tic = pyb.millis()