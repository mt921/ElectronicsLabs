import pyb

class PIDC:
    def __init__(self, Kp, Kd, Ki):
        self.Kp = Kp
        self.Kd = Kd
        self.Ki = Ki
        self.error_last = 0       # These are global variables to remember various states of controller
        self.tic = pyb.millis()
        self.error_sum = 0

    def getPWM(self, target, speed):

        # error input
        error = target - speed                      # e[n]
    
        # derivative input
        derivative = error - self.error_last        # error_dot. assume dt is constant
                                                    # 1/dt is absorbed into Kd
                                                    # this avoid division by small value

        toc = pyb.millis()
        dt = (toc-self.tic)*0.001                   # find dt as close to when used as possible
        # Integral input 
        self.error_sum += error*dt            
 
        #   Output 
        PID_output = (self.Kp * error) + (self.Ki * self.error_sum) + (self.Kd * derivative)

        # Store previous values 
        self.error_last = error
        self.tic = toc

        pwm_out = min(abs(PID_output), 100)         # Make sure pwm is less than 100 

        return pwm_out
