import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath('../src'))

try:
    from motor_control import MotorControl
    from vna_control import RSVNA
except (Exception,):
    raise

motors = MotorControl(kit_address=[0x61, 0x63], motor_id=[[0, 0], [1, 0]])
motors.init_motors()

vna = RSVNA()
vna.ip_address = '192.168.1.97'
vna.connect(link='lan')
# vna.setup(num_channels=2)

# NOTE: cannot load state !!!!
vna.load_state('20221011_2P_0p5_8p5_401_1KHz_test1.znx')

# set the inernals manually
vna._num_channels = 2
vna.freq_points = 401

# set motors on head
print(motors)
motors.set_on_head()
print(motors)

# ## create the problem
