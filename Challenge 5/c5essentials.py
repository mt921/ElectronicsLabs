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

class PIDC:
    def __init__(self, Kp, Kd, Ki):
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki
        self.error_last = 0       # These are global variables to remember various states of controller
        self.tic = pyb.millis()
        self.error_sum = 0

    def getPWM(self, target, pitch, pitch_dot):

        # error input
        error = target - pitch          # e[n]
    
        # derivative input
        derivative = -pitch_dot         # negative feedback

        toc = pyb.millis()
        dt = (toc-self.tic)*0.001       # find dt as close to when used as possible
        # Integration input 
        self.error_sum += error*dt            
 
        #   Output 
        PID_output = (self.Kp * error) + (self.Ki * self.error_sum) + (self.Ki * derivative)
        print(PID_output)
        # Store previous values 
        self.error_last = error
        self.tic = toc

        pwm_out = min(abs(PID_output), 100)             # Make sure pwm is less than 100 
 
        if PID_output > 0:                              # Output direction (need to check)
            direction = 'forward'
        elif PID_output < 0:
            direction = 'back'
        else: 
            direction = 'stop'

        return pwm_out, direction


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
pitch = 0
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

scale_1 = 5/9

tic = pyb.millis()	
while True:					
	toc = pyb.millis()
	alpha = 0.7    # larger = longer time constant
	pitch = int(imu.pitch())


	#pitch_speed = int(scale_1*pitch)
	
	pidc = PIDC(4.0,0.5,1.0)
	# new_pwm_A = pidc.getPWM(pitch_speed,A_speed)
	# new_pwm_B = pidc.getPWM(pitch_speed,B_speed)

	# if (pitch_speed >= 0):
	# 	A_forward(new_pwm_A)
	# 	B_forward(new_pwm_B)
	# else:
	# 	A_back(abs(new_pwm_A))
	# 	B_back(abs(new_pwm_B))

	# Display new speed
	oled.clear()
	oled.draw_text(0,10,'Pitch Angle:{:5d}'.format(pitch))
	oled.display()
	
	pyb.delay(100)
	tic = pyb.millis()