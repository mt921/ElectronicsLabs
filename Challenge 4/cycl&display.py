import pyb
import os
from pyb import Pin, Timer, ADC
from oled_938 import OLED_938
from mpu6050 import MPU6050

dance = []
f = open("danceydance.txt", "r")
moves = f.read().split(',')	
f.close()

A1 = Pin('X3', Pin.OUT_PP)		# Control direction of motor A
A2 = Pin('X4', Pin.OUT_PP)
PWMA = Pin('X1')				# Control speed of motor A
B1 = Pin('X7', Pin.OUT_PP)		# Control direction of motor B
B2 = Pin('X8', Pin.OUT_PP)
PWMB = Pin('X2')				# Control speed of motor B
b_LED = LED(4)					# Blue LED

# Configure timer 2 to produce 1KHz clock for PWM control
tim = Timer(2, freq = 1000)
motorA = tim.channel (1, Timer.PWM, pin = PWMA)
motorB = tim.channel (2, Timer.PWM, pin = PWMB)

# I2C connected to Y9, Y10 (I2C bus 2) and Y11 is reset low active
i2c = pyb.I2C(2, pyb.I2C.MASTER)
devid = i2c.scan()				# find the I2C device number
oled = OLED_938(
    pinout={"sda": "Y10", "scl": "Y9", "res": "Y8"},
    height=64, external_vcc=False, i2c_devid=i2c.scan()[0],
)
oled.poweron()
oled.init_display()

i = 0

tic = pyb.millis()	
while True:					
	toc = pyb.millis()
	alpha = 0.7    # larger = longer time constant

	oled.clear()
	oled.draw_text(0,30,str(moves[i]))
	oled.display()
	pyb.delay(300)
	i = i + 1
	
	tic = pyb.millis()
