#Below imports all neccessary packages to make this Python Script run
import time
import board
import matplotlib.pyplot as plt
import math
import numpy as np
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
import RPi.GPIO as GPIO
import time

#function that translates mm(distance) to motor steps
# one full rotetion (360deg.) of the motor corresponds to 200 steps (1.8deg./step)
#...which (for this lead screw) corresponds to 8mm linear distance
#dist=distance in mm, to be integer (e.g. 50)
def dist(dist):
     val=int(200*dist/8)
     return val

#GPIO.setmode(GPIO.BOARD)
GPIO.setup(4,GPIO.IN)

#assing motors to an address
#motor1 & 2, is kit1
#motor3 & 4, is kit2, etc
kit1 = MotorKit()
kit2 = MotorKit(address=0x61)
kit3 = MotorKit(address=0x62)
kit4 = MotorKit(address=0x63)

# If you uncomment below it will start by de-energising the Stepper Motor,
# Worth noting the final state the stepper motor is in is what will continue.
# Energised Stepper Motors get HOT over time along with the electronic silicon drivers

kit1.stepper1.release()
kit1.stepper2.release()
kit2.stepper1.release()
kit2.stepper2.release()
kit3.stepper1.release()
kit3.stepper2.release()
kit4.stepper1.release()
kit4.stepper2.release()

#prints initialization switch value
#1-closed circuit
#0-open circuit
# try:
# 	while True:
# 		readVal=GPIO.input(4)
# 		print(readVal)
# 		time.sleep(0.05)
# 	#	if readVal==True:
# 	#		print("initialization complete")
# 	#		GPIO.cleanup()
# 	#		break
# except KeyboardInterrupt:
# 	GPIO.cleanup()

#motors initialization
#initialization position is circle DIA-230mm
#motor_1 initialization
######################
#random long distance
rld=100
#small distance in front of switch
smd=10
# #######
for i in range(dist(smd)):
    kit1.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
kit1.stepper1.release()
######################
#motor_2 initialization
######################
# for i in range(dist(smd)):
#     kit1.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
# kit1.stepper2.release()
# ######################
# #motor_3 initialization
# ######################
# for i in range(dist(smd)):
#     kit2.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
# kit2.stepper1.release()
# ######################
# #motor_4 initialization
# ######################
# for i in range(dist(smd)):
#     kit2.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
# kit2.stepper2.release()
# ######################
# #motor_5 initialization
# ######################
# for i in range(dist(smd)):
#     kit3.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
# kit3.stepper1.release()
# ######################
#motor_6 initialization
######################
# for i in range(dist(smd)):
#     kit3.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
# kit3.stepper2.release()
# ######################
# #motor_7 initialization
# ######################
for i in range(dist(smd)):
    kit4.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
kit4.stepper1.release()
# ######################
# #motor_8 initialization
# ######################
for i in range(dist(smd)):
    kit4.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
kit4.stepper2.release()
# ######################

#gpio cleanup
GPIO.cleanup()

