# Below imports all neccessary packages to make this Python Script run
# import time
# import board
import matplotlib.pyplot as plt
import math
import numpy as np
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit
import RPi.GPIO as GPIO


# function that translates mm(distance) to motor steps
# one full rotation (360deg.) of the motor corresponds to 200 steps (1.8deg./step)
# ...which (for this lead screw) corresponds to 8mm linear distance
# dist=distance in mm, to be integer (e.g. 50)
def dist(steps):
    val = int(200 * steps / 8)
    return val


# reverse
def steps(motorsteps):
    val = int(8 * motorsteps / 200)
    return val


# GPIO.setmode(GPIO.BOARD)
GPIO.setup(4, GPIO.IN)

# assing motors to an address
# motor1 & 2, is kit1
# motor3 & 4, is kit2, etc

kit1 = MotorKit()
kit2 = MotorKit(address=0x61)
kit3 = MotorKit(address=0x62)
kit4 = MotorKit(address=0x63)

# If you uncomment below it will start by de-energising the Stepper Motor,
# Worth noting the final state the stepper motor is in is what will continue.
# Energised Stepper Motors get HOT over time along with the electronic silicon drivers

kit1.stepper1.release()  # motor1
kit1.stepper2.release()  # motor2
kit2.stepper1.release()  # motor3
kit2.stepper2.release()
kit3.stepper1.release()
kit3.stepper2.release()
kit4.stepper1.release()
kit4.stepper2.release()

# prints initialization switch value
# 1-closed circuit
# 0-open circuit

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

# motors initialization
# initialization position is circle DIA-230mm
# motor_1 initialization
######################
# random long distance
rld = 100
# small distance
smd = 1
smd_1 = 5
#######
for i in range(dist(rld)):
    kit1.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    # time.sleep(0.01)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_1 initialization complete")
        break
for i in range(dist(smd)):
    kit1.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit1.stepper1.release()
######################
# motor_2 initialization
######################
for i in range(dist(rld)):
    kit1.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_2 initialization complete")
        break
for i in range(dist(smd)):
    kit1.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit1.stepper2.release()
######################
# motor_3 initialization
######################
for i in range(dist(rld)):
    kit2.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_3 initialization complete")
        break
for i in range(dist(smd)):
    kit2.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit2.stepper1.release()
######################
# motor_4 initialization
######################
for i in range(dist(rld)):
    kit2.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_4 initialization complete")
        break
for i in range(dist(smd)):
    kit2.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit2.stepper2.release()
######################
# motor_5 initialization
######################
for i in range(dist(rld)):
    kit3.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_5 initialization complete")
        break
for i in range(dist(smd)):
    kit3.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit3.stepper1.release()
######################
# motor_6 initialization
######################
for i in range(dist(rld)):
    kit3.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_6 initialization complete")
        break
for i in range(dist(smd)):
    kit3.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit3.stepper2.release()
######################
# motor_7 initialization
######################
for i in range(dist(rld)):
    kit4.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_7 initialization complete")
        break
for i in range(dist(smd)):
    kit4.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit4.stepper1.release()
######################
# motor_8 initialization
######################
for i in range(dist(rld)):
    kit4.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_8 initialization complete")
        break
for i in range(dist(smd)):
    kit4.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
kit4.stepper2.release()
######################

# antenna positions at initialization (polar coordinates (radius in mm, angle in deg))
# initialization position is circle DIA-204mm
max_p = 102
ant_p_max = np.array([[max_p, max_p, max_p, max_p, max_p, max_p, max_p, max_p],
                      [0, 45, 90, 135, 180, 225, 270, 315]])  # initialization/max position
min_p = 65
ant_p_min = np.array(
    [[min_p, min_p, min_p, min_p, min_p, min_p, min_p, min_p], [0, 45, 90, 135, 180, 225, 270, 315]])  # min position
max_dif = max_p - min_p
############
# antenna and head poisiton arrays, just made with random values, they will be updated
ant_p = np.array(
    [[max_p, max_p, max_p, max_p, max_p, max_p, max_p, max_p], [0, 45, 90, 135, 180, 225, 270, 315]])  # antenna polar
ant_c = np.zeros((2, 8))  # antenna cartesian
head_p = np.array(
    [[max_p, max_p, max_p, max_p, max_p, max_p, max_p, max_p], [0, 45, 90, 135, 180, 225, 270, 315]])  # head polar
head_c = np.zeros((2, 8))  # head cartesian

# initialization on head
for i in range(dist(max_dif)):
    kit1.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_1 reach head")
        break
head_p[0][0] = max_p - steps(i)
ant_p[0][0] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit1.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit1.stepper1.release()
ant_p[0][0] = ant_p[0][0] + steps(i)

for i in range(dist(max_dif)):
    kit1.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_2 reach head")
        break
head_p[0][1] = max_p - steps(i)
ant_p[0][1] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit1.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit1.stepper2.release()
ant_p[0][1] = ant_p[0][1] + steps(i)

for i in range(dist(max_dif)):
    kit2.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_3 reach head")
        break
head_p[0][2] = max_p - steps(i)
ant_p[0][2] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit2.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit2.stepper1.release()
ant_p[0][2] = ant_p[0][2] + steps(i)

for i in range(dist(max_dif)):
    kit2.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_4 reach head")
        break
head_p[0][3] = max_p - steps(i)
ant_p[0][3] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit2.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit2.stepper2.release()
ant_p[0][3] = ant_p[0][3] + steps(i)

for i in range(dist(max_dif)):
    kit3.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_5 reach head")
        break
head_p[0][4] = max_p - steps(i)
ant_p[0][4] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit3.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit3.stepper1.release()
ant_p[0][4] = ant_p[0][4] + steps(i)

for i in range(dist(max_dif)):
    kit3.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_6 reach head")
        break
head_p[0][5] = max_p - steps(i)
ant_p[0][5] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit3.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit3.stepper2.release()
ant_p[0][5] = ant_p[0][5] + steps(i)

for i in range(dist(max_dif)):
    kit4.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_7 reach head")
        break
head_p[0][6] = max_p - steps(i)
ant_p[0][6] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit4.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit4.stepper1.release()
ant_p[0][6] = ant_p[0][6] + steps(i)

for i in range(dist(max_dif)):
    kit4.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    readVal = GPIO.input(4)
    if readVal == 0:
        print("motor_8 reach head")
        break
head_p[0][7] = max_p - steps(i)
ant_p[0][7] = max_p - steps(i)
for i in range(dist(smd_1)):
    kit4.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
kit4.stepper2.release()
ant_p[0][7] = ant_p[0][7] + steps(i)

# user input of position
print("select antennas posotions")
txt = input("input c for circle, e for ellipse or d to set distance from head: ")

if txt == "c":
    print("nothing")
#     dia=int(input("input circle diameter (max204, mim130) in mm, e.g. 200: "))
#     if dia>2*max_p or dia<2*min_p:
#         print("dia value out of range")
#         quit()
#     else:
#         circ=dia*np.ones((2,8))
#         circ[1]=ant_p[1]
#         diff=circ[0]-ant_p[0]
#         #diff=max_p-dia/2
#         #ant_p[0]=ant_p[0]-diff*np.ones((1,8))
#         #move motors
#         for i in range(dist(diff)):
#             kit1.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit1.stepper1.release()
#         for i in range(dist(diff)):
#             kit1.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit1.stepper2.release()
#         for i in range(dist(diff)):
#             kit2.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit2.stepper1.release()
#         for i in range(dist(diff)):
#             kit2.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit2.stepper2.release()
#         for i in range(dist(diff)):
#             kit3.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit3.stepper1.release()
#         for i in range(dist(diff)):
#             kit3.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit3.stepper2.release()
#         for i in range(dist(diff)):
#             kit4.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit4.stepper1.release()
#         for i in range(dist(diff)):
#             kit4.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit4.stepper2.release()
#
# #         print("pause 1")
# #         input("Press enter to continue")
#         #turn polar cord. to cartes. cord.
#         for i in range(len(ant_c[1])):
#             ant_c[0][i]=ant_p[0][i]*math.sin(math.pi/180.0*ant_p[1][i])
#             ant_c[1][i]=ant_p[0][i]*math.cos(math.pi/180.0*ant_p[1][i])
#
# #         print("pause 2")
# #         input("Press enter to continue")
#         #plot
#         theta=np.linspace(0,2*np.pi, 150)
#         radius=200
#         a=radius*np.cos(theta)
#         b=radius*np.sin(theta)
#         figure,axes=plt.subplots()
#         plt.plot(a,b)
#         plt.scatter(ant_c[0],ant_c[1])
#         axes.set_aspect(1)
#         plt.show()
# #########################################33
elif txt == "e":
    print("nothing")
#     dia1,dia2=input("input ellipse height and width in mm ,(max230,min160), e.g. 200 180: ").split()
#     dia1=int(dia1)
#     dia2=int(dia2)
#     if dia1>2*max_p or dia1<2*min_p or dia2>2*max_p or dia2<2*min_p:
#         print("values out of range")
#         quit()
#     else:
#         for i in range(len(ant_p[1])):
#             ant_p[0][i]=math.sqrt(1/((math.cos(math.pi/180.0*ant_p[1][i]))**2/(dia1/2)**2+(math.sin(math.pi/180.0*ant_p[1][i]))**2/((dia2/2)**2)))
#         #move motors
#         for i in range(dist(max_p-ant_p[0][0])):
#             kit1.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit1.stepper1.release()
#         for i in range(dist(max_p-ant_p[0][1])):
#             kit1.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit1.stepper2.release()
#         for i in range(dist(max_p-ant_p[0][2])):
#             kit2.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit2.stepper1.release()
#         for i in range(dist(max_p-ant_p[0][3])):
#             kit2.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit2.stepper2.release()
#         for i in range(dist(max_p-ant_p[0][4])):
#             kit3.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit3.stepper1.release()
#         for i in range(dist(max_p-ant_p[0][5])):
#             kit3.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit3.stepper2.release()
#         for i in range(dist(max_p-ant_p[0][6])):
#             kit4.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit4.stepper1.release()
#         for i in range(dist(max_p-ant_p[0][7])):
#             kit4.stepper2.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         kit4.stepper2.release()
#         #turn polar cord. to cartes. cord.
#         for i in range(len(ant_c[1])):
#             ant_c[0][i]=ant_p[0][i]*math.sin(math.pi/180.0*ant_p[1][i])
#             ant_c[1][i]=ant_p[0][i]*math.cos(math.pi/180.0*ant_p[1][i])
#         #plot
#         theta=np.linspace(0,2*np.pi, 150)
#         radius=200
#         a=radius*np.cos(theta)
#         b=radius*np.sin(theta)
#         figure,axes=plt.subplots()
#         plt.plot(a,b)
#         plt.scatter(ant_c[0],ant_c[1])
#         axes.set_aspect(1)
#         plt.show()
#################################
elif txt == "d":
    pass
#     ddist = int(input("input distance from head in mm, e.g. 5"))
#     if ddist > 20 or ddist < 0:
#         print("distance value out of range")
#         quit()
#     else:
#         # ant_p[0]=ant_p[0]-diff*np.ones((1,8)) #antenna position
#         # #move motors to head and to position
#         # for i in range(dist(rld)):
#         #     kit1.stepper1.onestep(direction=stepper.FORWARD,style=stepper.DOUBLE)
#         #     readVal=GPIO.input(x)
#         #     if readVal==0:
#         #         print("motor_1 contact")
#         #         break
#         # for i in range(dist(ddist)):
#         #     kit1.stepper1.onestep(direction=stepper.BACKWARD,style=stepper.DOUBLE)
#         # kit1.stepper1.release()
#         ######################################
#         # move motors to position
#         for i in range(dist(ddist)):
#             kit1.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
#         kit1.stepper1.release()
#         ant_p[0][0] = ant_p[0][0] - steps(i)
#         for i in range(dist(diff)):
#             kit1.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
#         kit1.stepper2.release()
#         ant_p[0][1] = ant_p[0][1] - steps(i)
#         for i in range(dist(diff)):
#             kit2.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
#         kit2.stepper1.release()
#         ant_p[0][2] = ant_p[0][2] - steps(i)
#         for i in range(dist(diff)):
#             kit2.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
#         kit2.stepper2.release()
#         ant_p[0][3] = ant_p[0][3] - steps(i)
#         for i in range(dist(diff)):
#             kit3.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
#         kit3.stepper1.release()
#         ant_p[0][4] = ant_p[0][4] - steps(i)
#         for i in range(dist(diff)):
#             kit3.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
#         kit3.stepper2.release()
#         ant_p[0][5] = ant_p[0][5] - steps(i)
#         for i in range(dist(diff)):
#             kit4.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
#         kit4.stepper1.release()
#         ant_p[0][6] = ant_p[0][6] - steps(i)
#         for i in range(dist(diff)):
#             kit4.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
#         kit4.stepper2.release()
#         ant_p[0][7] = ant_p[0][7] - steps(i)
# 
#         #         print("pause 1")
#         #         input("Press enter to continue")
#         # turn polar cord. to cartes. cord.
#         for i in range(len(ant_c[1])):
#             ant_c[0][i] = ant_p[0][i] * math.sin(math.pi / 180.0 * ant_p[1][i])
#             ant_c[1][i] = ant_p[0][i] * math.cos(math.pi / 180.0 * ant_p[1][i])
#             head_c[0][i] = head_p[0][i] * math.sin(math.pi / 180.0 * head_p[1][i])
#             head_c[1][i] = head_p[0][i] * math.cos(math.pi / 180.0 * head_p[1][i])
# 
#         #         print("pause 2")
#         #         input("Press enter to continue")
#         # plot
#         theta = np.linspace(0, 2 * np.pi, 150)
#         radius = 200
#         a = radius * np.cos(theta)
#         b = radius * np.sin(theta)
#         figure, axes = plt.subplots()
#         plt.plot(a, b)
#         plt.scatter(ant_c[0], ant_c[1])
#         plt.scatter(head_c[0], head_c[1])
#         axes.set_aspect(1)
#         plt.show()


# print("pause_3")
# input("press enter to cont.")
# 
# #############################################################
# 
# # vna code
# 
# #############################################################
# 
# print("pause_4")
# input("press enter to cont.")
# # go back
# 
# 
# # gpio cleanup
GPIO.cleanup()
