import pyb
from pyb import Pin, Timer, ADC
from oled_938 import OLED_938
from mpu6050 import MPU6050

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

def A_forward(value):
	A1.low()
	A2.high()
	motorA.pulse_width_percent(value)

def A_back(value):
	A2.low()
	A1.high()
	motorA.pulse_width_percent(value)
	
def A_stop():
	A1.high()
	A2.high()
	
def B_forward(value):
	B2.low()
	B1.high()
	motorB.pulse_width_percent(value)

def B_back(value):
	B1.low()
	B2.high()
	motorB.pulse_width_percent(value)
	
def B_stop():
	B1.high()
	B2.high()
	
# Initialise variables
speed = 0
A_speed = 0
A_count = 0
B_speed = 0
B_count = 0

# IMU connected to X9 and X10
imu = MPU6050(1, False)    	# Use I2C port 1 on Pyboard
		
#-------  Section to set up Interrupts ----------
def isr_motorA(dummy):	# motor A sensor ISR - just count transitions
	global A_count
	A_count += 1

def isr_motorB(dummy):	# motor B sensor ISR - just count transitions
	global B_count
	B_count += 1
		
def isr_speed_timer(dummy): 	# timer interrupt at 100msec intervals
	global A_count
	global A_speed
	global B_count
	global B_speed
	A_speed = A_count			# remember count value
	B_speed = B_count
	A_count = 0					# reset the count
	B_count = 0
	
# Create external interrupts for motorA Hall Effect Senor
import micropython
micropython.alloc_emergency_exception_buf(100)
from pyb import ExtInt

motorA_int = ExtInt ('Y4', ExtInt.IRQ_RISING, Pin.PULL_NONE,isr_motorA)
motorB_int = ExtInt ('Y6', ExtInt.IRQ_RISING, Pin.PULL_NONE,isr_motorB)

# Create timer interrupts at 100 msec intervals
speed_timer = pyb.Timer(4, freq=10)
speed_timer.callback(isr_speed_timer)

#-------  END of Interrupt Section  ----------

tic = pyb.millis()	
while True:			
	toc = pyb.millis()
	alpha = 0.7    # larger = longer time constant
	pitch = int(imu.pitch())
	roll = int(imu.roll())
	
	#maximum speed will be at 180, which should correspond to 100% motor drive
	#update code so that pitch & roll angles map correctly to percentage motor drive 
	#because the mapping is not correct, the motors will not spin for negative angle values
	#therefore this needs to be updated ^
	pitch_speed = int(pitch)
	roll_speed = int(roll)
	if (speed >= 0):		# forward
		A_forward(pitch_speed)
		B_forward(roll_speed)
	else:
		A_back(abs(pitch_speed))
		B_back(abs(roll_speed))

	# Display new speed
	oled.clear()
	oled.draw_text(0,10,'Pitch Angle:{:5d}'.format(pitch))
	oled.draw_text(0,20,'Roll Angle{:5d}'.format(roll))
	oled.draw_text(0,30,'Motor A drive:{:5.2f}%'.format(A_speed))	
	oled.draw_text(0,40,'Motor B drive:{:5.2f}%'.format(B_speed))	
	oled.display()
	
	pyb.delay(100)
	tic = pyb.millis()