import time
import matplotlib.pyplot as pp

try:
    from adafruit_motorkit import MotorKit
    from adafruit_motor import stepper
    import RPi.GPIO as GPIO
except (Exception,):
    _has_pi = False

pin_number = 17
seconds = 20

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
pin = []

t_end = time.time() + seconds

length = 0
while time.time() < t_end:
    pin.append(GPIO.input(pin_number))
    print(pin[-1])

pp.plot(pin)
pp.show()