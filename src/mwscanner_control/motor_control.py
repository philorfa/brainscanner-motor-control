import numpy as np
import warnings
from sympy import solve, var
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
from .util import dist2coordinates, pause, outer_ellipsoid_fit

matplotlib.use("TkAgg")

_has_pi = True

# MOTOR PARAMETERS #

_NUM_CONTROLS = 17

# Max distance the motor can cover with the current hardware (in mm)
# Antenna = [0, 1, 2, 3, 4, 5, 6, 7]
_DRIVERS_MAX = [40, 40, 40, 40, 40, 40, 40, 40]

# !!!!!!!!! THE FOLLOWING MEASUREMENTS MUST BE ACCURATE !!!!!!!!! #

# Distance of each pair of antennas (in mm) in close position

# Antenna = [0, 1, 2, 3,
#            4, 5, 6, 7]

# 0-4: 139
# INN_DIST04 = 139
#
# # 1-5: 122
# INN_DIST15 = 122
#
# # 2-6: 122
# INN_DIST26 = 122
#
# # 3-7: 120
# INN_DIST37 = 120
#
# # Distance of each antenna from the center (in mm) in close position
# INNER_DIST = [INN_DIST04/2, INN_DIST15/2, INN_DIST26/2, INN_DIST37/2,
#               INN_DIST04/2, INN_DIST15/2, INN_DIST26/2, INN_DIST37/2]

# Distance of each pair of antennas (in mm) in home position

# Antenna = [0, 1, 2, 3,
#            4, 5, 6, 7]

# 0-4 : 221
_OUT_DIST04 = 221

# 1-5: 204
_OUT_DIST15 = 204

# 2-6: 204
_OUT_DIST26 = 204

# 3-7: 200
_OUT_DIST37 = 200

# Distance of each antenna from the center (in mm) in home position
_OUTER_DIST = [_OUT_DIST04 / 2, _OUT_DIST15 / 2, _OUT_DIST26 / 2, _OUT_DIST37
               / 2, _OUT_DIST04 / 2, _OUT_DIST15 / 2, _OUT_DIST26 / 2,
               _OUT_DIST37 / 2]

# MAX distance allowed of each antenna from the center (in mm) in close position
_INNER_DIST = [_OUTER_DIST[0] - _DRIVERS_MAX[0],
               _OUTER_DIST[1] - _DRIVERS_MAX[1],
               _OUTER_DIST[2] - _DRIVERS_MAX[2],
               _OUTER_DIST[3] - _DRIVERS_MAX[3],
               _OUTER_DIST[4] - _DRIVERS_MAX[4],
               _OUTER_DIST[5] - _DRIVERS_MAX[5],
               _OUTER_DIST[6] - _DRIVERS_MAX[6],
               _OUTER_DIST[7] - _DRIVERS_MAX[7]]

# Angle of each antenna (in degrees)
# Antenna = [0, 1, 2, 3, 4, 5, 6, 7]
_ANGLES = [90, 45, 0, 315, 270, 225, 180, 135]

try:
    from adafruit_motorkit import MotorKit
    from adafruit_motor import stepper
    import RPi.GPIO as GPIO
except (Exception,):
    _has_pi = False


# TODO : CHECK POSITION AFTER RELEASE


class MotorControl:
    """Constructor method for the motor controller object:

    This method initializes the motor controller object with the
    provided kit addresses and motor IDs. It also sets up the initial
    positions, antenna numbers, and motor coordinates.

    Args:
        kit_address (list, optional): List of kit addresses (default: None).
        motor_id (list, optional): List of motor IDs (default: None).

    Example:
        >>> obj = MotorControl(kit_address=[0x60, 0x61],
        >>>                    motor_id=[[0, 0],[0, 1]])

    Note:
        - If `kit_address` is not provided, it is set to the default
          addresses [0x60, 0x61, 0x62, 0x63].
        - If `motor_id` is not provided, it is set to the default IDs
          [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1], [3, 0], [3, 1]].
        - The `kit_address` and `motor_id` parameters are used to keep track
          of the hats and motors.
        - The initial motor positions are set to the maximum value defined
          by `_DRIVERS_MAX`.
        - The `_antenna_number` sets the numbering that we have set
          to the lab
        - The antenna numbers and motor coordinates are initialized based on
          the kit addresses and motor IDs.
        - The GPIO pin for the switch is set up.


    Destructor method for the motor controller object:

    This method is called when the object is being destroyed. It releases
    all the motors and cleans up the GPIO pins if Raspberry Pi libraries
    are available.

    Example:
        >>> obj = MotorControl()
        >>> del obj

    Note:
        - This method is automatically called by the Python interpreter and
          should not be called directly.
        - It releases all the motors by calling the `release_all` method.
        - If Raspberry Pi libraries are available, it also cleans up the
          GPIO pins using `GPIO.cleanup`.

    Representation method for the motor controller object:

    Returns a string representation of the motor controller object.

    This method returns a string that contains information about the motors,
    including their numbering, addresses, positions, and coordinates.
    If the system is not initialized, it indicates that positions are not
    available before initialization.

    Returns:
        str: A string representation of the motor controller object.

    Example:
        >>> obj = MotorControl()
        >>> print(obj)
        Motor: 0
        Numbering: 2
        Address: 0x61
        Stepper: 1
        Position: 100 mm
        Coordinates: (10.0, 20.0)
        --------------
        Motor: 1
        Numbering: 3
        Address: 0x61
        Stepper: 1
        Position: 200 mm
        Coordinates: (15.0, 25.0)
        --------------
        ...
    """

    def __init__(self, kit_address=None,
                 motor_id=None):
        # keep track of the hats and the motors
        if kit_address is None:
            kit_address = [0x60, 0x61, 0x62, 0x63]
        if motor_id is None:
            motor_id = [[0, 0], [0, 1],
                        [1, 0], [1, 1],
                        [2, 0], [2, 1],
                        [3, 0], [3, 1]]
        self._kit_address = kit_address
        self._motor_id = motor_id

        self._antenna_number = []
        self._antenna_coords = []
        self._antenna_pos = []
        for im in range(len(self._motor_id)):

            # set the numbering of the antennas

            # First kit
            if self._kit_address[self._motor_id[im][0]] == 0x60:
                if self._motor_id[im][1] == 0:
                    self._antenna_number.append(0)
                else:
                    self._antenna_number.append(1)
            # Second kit
            elif self._kit_address[self._motor_id[im][0]] == 0x61:
                if self._motor_id[im][1] == 0:
                    self._antenna_number.append(2)
                else:
                    self._antenna_number.append(3)
            # Third kit
            elif self._kit_address[self._motor_id[im][0]] == 0x62:
                if self._motor_id[im][1] == 0:
                    self._antenna_number.append(4)
                else:
                    self._antenna_number.append(5)
            # Fourth kit
            else:
                if self._motor_id[im][1] == 0:
                    self._antenna_number.append(6)
                else:
                    self._antenna_number.append(7)

            # position in mm
            self._antenna_pos.append(_OUTER_DIST[self._antenna_number[im]])

            # set real coordinates of motors
            self._antenna_coords.append(
                dist2coordinates(self._antenna_pos[im], self.get_angle(im)))

        self._init_system = False

        self._pin_switch = _NUM_CONTROLS

        self.plot_pin_states = False

        # init the motors

        if not _has_pi:
            msg = 'Raspberry Pi libraries could not be found, Motors cannot ' \
                  'be imported to the system'
            warnings.warn(msg, UserWarning)
            print(msg)
        else:

            self._mkits = [MotorKit(add) for add in self._kit_address]
            self._steppers = []
            for mid in self._motor_id:
                attr = 'stepper1' if mid[1] == 0 else 'stepper2'
                mkit = self._mkits[mid[0]]
                self._steppers.append(getattr(mkit, attr))

            # how many times to check if the switch is off
            self.pin_checks = 10

            # init the GPIO
            # print("Gpio mode (10 board, 11 bcm)", GPIO.getmode())
            GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self._pin_switch, GPIO.IN)
            GPIO.setup(self._pin_switch, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def __del__(self):
        """Destructor method for the motor controller object.

        This method is called when the object is being destroyed. It
        releases all the motors and cleans up the GPIO pins if Raspberry Pi
        libraries are available.

        Example:
            >>> obj = MotorControl()
            >>> del obj

        Note:
            - This method is automatically called by the Python interpreter
              and should not be called directly.
            - It releases all the motors by calling the `release_all`
              method.
            - If Raspberry Pi libraries are available, it also cleans up
              the GPIO pins using `GPIO.cleanup`.
        """
        # print("Terminating ...")
        if _has_pi:
            self.release_all()
            GPIO.cleanup()

    def __str__(self):
        """Returns a string representation of the motor controller object.

        This method returns a string that contains information about the
        motors, including their numbering, addresses, positions, and
        coordinates. If the system is not initialized, it indicates that
        positions are not available before initialization.

        Returns:
            str: A string representation of the motor controller object.

        Example:
            >>> obj = MotorControl()
            >>> print(obj)

        Output:
            Motor: 0
            Numbering: 2
            Address: 0x61
            Stepper: 1
            Closer Distance: 70.5 mm
            Position: 100 mm
            Coordinates: (10.0, 20.0)
            --------------
            Motor: 1
            Numbering: 3
            Address: 0x61
            Stepper: 1
            Closer Distance: 60 mm
            Position: 200 mm
            Coordinates: (15.0, 25.0)
            --------------
            ...
        """
        motor_str = ''
        if not self._init_system:
            motor_str += 'Positions are not available before initialization'

        for im in range(len(self._steppers)):
            motor_str += '______________\n'
            motor_str += 'Motor: {:d}\n'.format(im)
            motor_str += 'Numbering: {:d}\n'.format(self._antenna_number[im])
            motor_str += 'Address: {:x}\n' \
                .format(self._kit_address[self._motor_id[im][0]])
            motor_str += 'Stepper: {:d}\n'.format(self._motor_id[im][0])
            motor_str += 'Closer Distance: {:2f}\n'.format(
                _INNER_DIST[self._antenna_number[im]])

            if self._init_system:
                motor_str += 'Position: {:2f} mm\n'.format(self._antenna_pos[
                                                               im])
                motor_str += 'Coordinates: ({:2f},{:2f}) \n' \
                    .format(self._antenna_coords[im][0],
                            self._antenna_coords[im][1])
        motor_str += '______________\n'

        return motor_str

    @staticmethod
    def _dist2steps(distance):
        """Converts distance (in mm ) to the equivalent number of motor steps.

        Args:
            distance (float): The distance in mm.

        Returns:
            int: The number of steps.

        Example:
            >>> _dist2steps(10)
            250

        Note:
            one full rotation (360deg.) of the motor corresponds to 200 steps
            (1.8deg./step) which (for this lead screw) corresponds to 8mm linear
            distance
        """
        return int(200 * distance / 8)

    @staticmethod
    def _steps2dist(steps):
        """Converts motor steps to linear distance (mm)

        Args:
            steps (int): The number of motor steps.

        Returns:
            float: The distance in mm.

        Example:
            >>> steps2dist(500)
            20
        """
        return 8 * steps / 200

    @staticmethod
    def _update_move(distance):
        """Print a message indicating the movement based on the given distance.

        Args:
            distance (float): The distance of movement.

        Examples:
            >>> _update_move(10.5)
            # Prints 'Moved Forward: 10.500000 mm'

            >>> _update_move(-5.2)
            # Prints 'Moved Backward: 5.200000 mm'

            >>> _update_move(0)
            # Prints 'Antenna stayed Still'

        Notes:
            - Positive distance indicates forward movement.
            - Negative distance indicates backward movement.
            - A distance of 0 indicates no movement.
        """
        if distance > 0:
            print('Moved Forward: {:2f} mm'.format(distance))
        elif distance < 0:
            print('Moved Backward: {:2f} mm'.format(abs(distance)))
        else:
            print('Antenna stayed Still')

    @property
    def coordinates(self):
        """Get coordinates"""
        return self._antenna_coords

    def check_pin(self, pin_value):
        """Checks the status of a pin switch.

        If the pin switch is OFF, it prints "switch is OFF".
        If the pin switch is STILL ON, it prints "switch is STILL ON",
        terminates the program, and exits.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.check_pin()
            switch is OFF
        """
        for _ in range(3):

            pin_value.append(GPIO.input(self._pin_switch))
            if pin_value[-1] == 1:
                print("switch is OFF")
                return pin_value
            else:
                print("switch is STILL ON")

        print("3 times in a row")
        print(">Terminating...")
        self.__del__()
        sys.exit()

    def pin_status(self):
        """Checks and prints the status of a pin switch.

        If the pin switch is ON, it prints "switch is ON".
        If the pin switch is OFF, it prints "switch is OFF".

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.pin_status()
            switch is OFF
        """
        if GPIO.input(self._pin_switch) == 0:
            print("switch is ON")
        else:
            print("switch is OFF")

    def plot_ellipse_antennas(self, x_coordinates, y_coordinates):
        """Plots an ellipse and antennas on a coordinate system.

        Args:
            x_coordinates (list): The x-coordinates of the ellipse.
            y_coordinates (list): The y-coordinates of the ellipse.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> coordinates_x = [1, 2, 3, 4, 5]
            >>> coordinates_y = [2, 4, 6, 8, 10]
            >>> obj.plot_ellipse_antennas(coordinates_x, coordinates_y)
            (Plot is displayed showing the ellipse and antennas)
        """
        x_val = [x[0] for x in self._antenna_coords]
        y_val = [x[1] for x in self._antenna_coords]

        x_coordinates.append(x_coordinates[0])
        y_coordinates.append(y_coordinates[0])

        plt.figure()
        plt.plot(x_coordinates, y_coordinates,
                 color='r',
                 lw=1.5,
                 zorder=1,
                 label='ellipse')
        plt.scatter(x_val, y_val, s=150, color='b', zorder=2, label='antennas')
        plt.gca().axis('equal')
        plt.legend()

        plt.show()

    def show_antennas(self):
        """Displays the positions of antennas on a coordinate system.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.show_antennas()
            (Plot is displayed showing the positions of antennas)
        """
        x_val = [x[0] for x in self._antenna_coords]
        y_val = [x[1] for x in self._antenna_coords]

        fig, plot = plt.subplots()

        plt.scatter(x_val, y_val, s=100)
        for i, _ in enumerate(x_val):
            plot.annotate("{:d} ({:.1f},{:.1f})".format(i, x_val[i], y_val[i]),
                          xy=(x_val[i], y_val[i]),
                          xytext=(x_val[i] + 5, y_val[i]))

        plt.gca().axis('equal')

        plt.show()

    def release_all(self):
        """Releases all the steppers.

        This method releases all the stepper motors associated with the
        instance of the class.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.release_all()
            (All steppers are released)
        """
        for stpr in self._steppers:
            stpr.release()

    def get_angle(self, motor_num):
        """Retrieves the angle corresponding to a specific motor number.

        This method takes a motor number as input and returns the
        corresponding angle from the `_ANGLES` list based on the
        `_antenna_number` mapping.

        Args:
            motor_num (int): The motor number.

        Returns:
            float: The angle in degrees.

        Example:
            >>> obj = MotorControl()
            >>> obj.get_angle(2)
            45.0
        """
        return _ANGLES[self._antenna_number[motor_num]]

    def check_pin_stable(self, pin_value):
        """Checks if the pin state is stable.

        This function monitors the state of a GPIO pin, and prints messages
        indicating the state  of the pin at two different points in time.
        It also issues a warning if the pin state  is not stable,
        suggesting to initialize the antennas until the warning does not
        appear.

        Raises:
            UserWarning: If the state of the GPIO pin is unstable.
        """
        pre_time = datetime.now()
        pin_value.append(GPIO.input(self._pin_switch))
        pin_value.append(GPIO.input(self._pin_switch))
        if pin_value[-1] != pin_value[-2]:
            now_time = datetime.now()
            if pin_value[-2] == 0:
                print(pre_time, "GPIO PIN was ", pin_value[-2], ", SWITCH was "
                                                                "PRESSED, "
                                                                "LED was OFF")
                print(now_time, "GPIO PIN was ", pin_value[-1], ", SWITCH was "
                                                                "NOT PRESSED, "
                                                                "LED was ON")
            else:
                print(pre_time, "GPIO PIN was ", pin_value[-2], ", SWITCH was "
                                                                "NOT PRESSED, "
                                                                "LED was ON")
                print(now_time, "GPIO PIN was ", pin_value[-1], ", SWITCH was "
                                                                "PRESSED, "
                                                                "LED was OFF")
            msg = "Switch status is not stable, STRONG SUGGESTION: INITIALIZE " \
                  "ANTENNAS until the msg doesnt appear"
            warnings.warn(msg, UserWarning)
            print(msg)

        return pin_value

    def move_switch_off(self, num_motor, pin_value, steps=0, forward=True,
                        verbose=True):
        """Moves the switch off by controlling the motor.

        This method moves the switch off by controlling the specified motor.
        It checks the status of the switch using the GPIO pin. If the
        switch is off, it returns the distance traveled in millimeters
        based on the number of steps. The motor can be moved forward or
        backward depending on the `forward` parameter.

        Args:
            pin_value:
            num_motor (StepperMotor): The stepper motor object to control.
            steps (int, optional): The initial number of steps, defaults to
                                   0.
            forward (bool, optional): Flag indicating the direction of
            movement. Defaults to True.
            verbose (bool, optional): Flag indicating whether to print
            verbose output. Defaults to True.

        Returns:
            int: The distance traveled in millimeters in order to release
            the switch.

        Example:
            >>> obj = MotorControl()
            >>> kit = MotorKit()
            >>> motor_ant = kit.stepper1
            >>> obj.move_switch_off(motor=motor_ant, forward=True)
            10

        Note:
            The method checks the status of the switch using the GPIO pin
            `self._pin_switch`.
            It uses the `dist2steps` and `steps2dist` functions to convert
            between steps and distance.
            The `StepperMotor` class should be instantiated and passed as an
            argument to control the motor.
            The `forward` parameter determines the direction of movement
            (forward or backward).
        """
        pin_value.append(GPIO.input(self._pin_switch))
        if pin_value[-1] == 0:

            if verbose:
                print("Moving to release switch")

            pin_value.append(GPIO.input(self._pin_switch))
            while pin_value[-1] == 0:
                if forward:
                    self.forward(num_motor)
                else:
                    self.backward(num_motor)

                steps += 1

                pin_value = self.check_pin_stable(pin_value=pin_value)

        pin_value.append(GPIO.input(self._pin_switch))
        if pin_value[-1] == 0:
            print("Switch is still ON")

        return steps, pin_value

    def new_position(self, num_motor, distance):
        """Updates the position and coordinates of a motor.

        This method updates the position of a motor identified by
        `num_motor` with the specified `distance`. It updates the
        `_antenna_pos` ON THE DRIVER (0-41) and `_antenna_coords`
        dictionaries accordingly, using the `dist2coordinates` function to
        calculate the new coordinates based on the distance, angle,
        and antenna number.

        Args:
            num_motor (int): The motor number.
            distance (float): The new position for the motor.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.new_position(1, 10)
            (Position and coordinates of motor 1 are updated)
        """
        self._antenna_pos[num_motor] = distance
        self._antenna_coords[num_motor] = \
            dist2coordinates(distance,
                             self.get_angle(num_motor))

    def forward(self, num_motor):
        """Moves the specified stepper motor one step forward.

        Args:
            num_motor (int): The index of the stepper motor to be moved.

        Note:
            The new position of the antenna is updated with respect to
            the number of steps taken.
        """
        self._steppers[num_motor].onestep(
            direction=stepper.FORWARD, style=stepper.DOUBLE)

        self.new_position(num_motor,
                          self._antenna_pos[
                              num_motor] - self._steps2dist(1))

    def force_forward(self, num_motor, distance):
        """Forces the specified stepper motor to move forward by a certain
            distance.

        Args:
            num_motor (int): The index of the stepper motor to be moved.
            distance (int): The distance to be moved in millimeters.

        Note:
            The distance is converted to steps before moving the motor.
            The motor is released after moving.
        """
        for _ in range(self._dist2steps(distance)):
            self._steppers[num_motor].onestep(direction=stepper.FORWARD,
                                              style=stepper.DOUBLE)
        self._steppers[num_motor].release()

    def backward(self, num_motor):
        """Moves the specified stepper motor one step backward.

        Args:
            num_motor (int): The index of the stepper motor to be moved.

        Note:
            The new position of the antenna is updated with respect to
            the number of steps taken.
        """
        self._steppers[num_motor].onestep(
            direction=stepper.BACKWARD, style=stepper.DOUBLE)

        self.new_position(num_motor,
                          self._antenna_pos[
                              num_motor] + self._steps2dist(1))

    def force_backward(self, num_motor, distance):
        """Forces the specified stepper motor to move backward by a certain
            distance.

        Args:
            num_motor (int): The index of the stepper motor to be moved.
            distance (int): The distance to be moved in millimeters.

        Note:
            The distance is converted to steps before moving the motor.
            The motor is released after moving.
        """
        for _ in range(self._dist2steps(distance)):
            self._steppers[num_motor].onestep(direction=stepper.BACKWARD,
                                              style=stepper.DOUBLE)
        self._steppers[num_motor].release()

    def init_motors(self, pauses=True, plot_pin=False):
        """Initializes motors to HOME position

        Initializes each motor in the `_steppers` list by sequentially
        moving each motor backward until it touches the switch connected
        to the GPIO pin. Afterwards, it moves a few steps forward to
        release the switch. Each motor is released after its
        initialization, accompanied by a status message of the PIN/switch
        state.

        Args:
            pauses (bool, optional): Flag to decide whether to pause after
            each motor initialization. Defaults to True.

            plot_pin (bool, optional): Flag to decide whether to plot pin
            status during initialization , after the process is done.
            Defaults to False.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.init_motors(pauses=True)
            (Motor initialization process is performed)

        Note:
            This method leverages `dist2steps`, `move_switch_off`,
            `check_pin`, `new_position`, and `pause` methods to carry out
            motor initialization.
            It uses the GPIO input to ascertain the switch status. The
            initialization involves moving the motor backward until the
            switch is activated, and then advancing it to release the
            switch. The `pauses` parameter can be utilized to control
            pauses after each motor's initialization. Once the process is
            completed, self._init_system is set to True, indicating that the
            positions of the motors are now known.
        """
        print("---------------------")
        print("INITIALIZING MOTORS")
        print("---------------------\n")

        all_pin_value = []
        for num_motor in range(len(self._motor_id)):

            pin_value = []
            steps_switch_off = 0

            print("----- Antenna {:d} -----".format(
                self._antenna_number[num_motor]))

            print("Moving BACKWARD")
            while True:

                self._steppers[num_motor].onestep(
                    direction=stepper.BACKWARD, style=stepper.DOUBLE)

                pin_value.append(GPIO.input(self._pin_switch))

                if pin_value[-1] == 0:
                    plot_pin = self.plot_pin_states
                    print("Pressed switch")

                    for _ in range(self.pin_checks):
                        extra_steps, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=True)

                        steps_switch_off += extra_steps

                    pin_value.append(GPIO.input(self._pin_switch))
                    if pin_value[-1] == 1:

                        print("Switch released, {:2f} mm needed".format(
                            self._steps2dist(steps_switch_off)))
                        break
                    else:
                        msg = "Unstable Switch State, Repeat Initialization"
                        warnings.warn(msg, UserWarning)
                        print(msg)
                        _, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=True)

            print('Initialization complete')

            self._steppers[num_motor].release()

            pin_value = self.check_pin(pin_value)
            all_pin_value.append(pin_value)

            self.new_position(num_motor, _OUTER_DIST[self._antenna_number[
                num_motor]])

            if pauses:
                pause()

        if plot_pin:
            fig, axs = plt.subplots(len(self._motor_id), figsize=(10, 20))
            for ant, pnv in enumerate(all_pin_value):
                axs[ant].plot(pnv)
                axs[ant].set_title("Antenna: " + str(ant))
            fig.tight_layout(pad=5.0)
            plt.show()
        self._init_system = True

    def set_on_head(self, pauses=True, plot_pin=False):
        """Moves each motor until it touches the head

        Moves each motor in the `_steppers` list forward until it touches the head by
        repeatedly making forward steps. Once the switch connected to the GPIO pin is
        activated, the motor takes a few steps backward to release the switch.

        Args:
            plot_pin:
            pauses (bool, optional): A flag determining whether to pause after each
            motor movement. Defaults to True.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.set_on_head(pauses=True)
            (Each motor in the list moves to touch the head)

        Note:
            This method employs the `dist2steps`, `move_switch_off`, `check_pin`,
            `new_position`, and `pause` methods to implement the motor movement. It
            uses the GPIO input to check the switch status. The movement process
            entails advancing the motor until the switch is pressed, followed by a
            backward movement to release the switch. After this process, the position
            of each motor is updated. The `pauses` parameter can be used to manage
            pauses after each motor movement.
        """
        print("---------------------")
        print("FINDING HEAD")
        print("---------------------\n")

        self.init_motors(pauses=False)
        all_pin_value = []
        for num_motor in range(len(self._motor_id)):

            pin_value = []
            steps_switch_off = 0

            init_pos = self._antenna_pos[num_motor]

            print("----- Antenna {:d} -----".format(
                self._antenna_number[num_motor]))

            found_head = False
            max_distance = _DRIVERS_MAX[self._antenna_number[num_motor]]

            print("Moving FORWARD")

            for steps in range(self._dist2steps(max_distance)):

                self.forward(num_motor)

                pin_value.append(GPIO.input(self._pin_switch))
                if pin_value[-1] == 0:
                    plot_pin = self.plot_pin_states
                    print("Pressed switch")

                    for _ in range(self.pin_checks):
                        extra_steps, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=False)

                        steps_switch_off += extra_steps

                    pin_value.append(GPIO.input(self._pin_switch))
                    if pin_value[-1] == 1:

                        print("Switch released, {:2f} mm needed".format(
                            self._steps2dist(steps_switch_off)))

                        print('Antenna is set on head')

                        found_head = True
                        break
                    else:
                        msg = "Unstable Switch State, Repeat Initialization"
                        warnings.warn(msg, UserWarning)
                        print(msg)
                        _, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=True)

            if not found_head:
                print('Antenna did NOT find head')

            self._steppers[num_motor].release()

            pin_value = self.check_pin(pin_value)
            all_pin_value.append(pin_value)

            self._update_move(init_pos - self._antenna_pos[num_motor])

            if pauses:
                pause()

        if plot_pin:
            fig, axs = plt.subplots(len(self._motor_id), figsize=(10, 20))
            for ant, pnv in enumerate(all_pin_value):
                axs[ant].plot(pnv)
                axs[ant].set_title("Antenna: " + str(ant))
            fig.tight_layout(pad=5.0)
            plt.show()

    def move_forward(self, motor, distance, pauses=True, plot_pin=False):
        """Moves motor forward

        This method moves the specified motor forward towards the head for
        the specified distance in millimeters. If the distance is larger
        than the maximum distance that the motor can move (_DRIVERS_MAX),
        the motor will move until it reaches the end. While moving forward,
        if the head is detected (based on the switch status), the motor
        will back off until the switch is released.

        If the value of the `motor` parameter is 100, the method moves all
        the motors in the `_steppers` list the same distance.

        Args:
            plot_pin:
            motor (int): The motor number or 100 to move all motors.
            distance (float): The distance in millimeters to move the motor
            forward.
            pauses (bool, optional): Flag indicating whether to pause after
            each motor movement. Defaults to True.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.move_forward(motor=1, distance=10, pauses=True)
            (Motor movement forward is performed)`

        Note:
            - The method utilizes the `dist2steps`, `move_switch_off`,
              `check_pin`, `new_position`, and `pause` methods to perform
              the motor movement.
            - The method takes into account the maximum distance that the
              motor can move (_DRIVERS_MAX) and adjusts the distance if it
              exceeds this limit.
            - The method checks the switch status using the GPIO input to
              detect the head.
            - After each motor movement, the method checks the pin status
              using the `check_pin` method.
            - The `new_position` method is used to update the motor position
              based on the distance and back_distance.
            - Pauses after each motor movement can be controlled using the
              `pauses` parameter.
        """
        print("---------------------")
        print("FORWARD")
        print("---------------------\n")

        start_motor = motor
        end_motor = motor + 1
        if motor == 100:
            start_motor = 0
            end_motor = len(self._steppers)
        all_pin_value = []
        for num_motor in range(start_motor, end_motor):

            pin_value = []
            steps_switch_off = 0

            init_pos = self._antenna_pos[num_motor]

            print("----- Antenna {:d} -----".
                  format(self._antenna_number[num_motor]))

            if self._antenna_pos[num_motor] - distance < \
                    _INNER_DIST[self._antenna_number[num_motor]]:
                print("> Antenna CANNOT MOVE THAT CLOSE, reaching closest "
                      "point")

                distance = self._antenna_pos[num_motor] - _INNER_DIST[
                    self._antenna_number[num_motor]]

            print("Moving FORWARD")

            for _ in range(self._dist2steps(distance)):

                self.forward(num_motor)

                pin_value.append(GPIO.input(self._pin_switch))
                if pin_value[-1] == 0:

                    plot_pin = self.plot_pin_states
                    print("Pressed switch")

                    for _ in range(self.pin_checks):
                        extra_steps, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=False)

                        steps_switch_off += extra_steps

                    pin_value.append(GPIO.input(self._pin_switch))
                    if pin_value[-1] == 1:

                        print("Switch released, {:2f} mm needed".format(
                            self._steps2dist(steps_switch_off)))
                        break
                    else:
                        msg = "Unstable Switch State, Repeat Initialization"
                        warnings.warn(msg, UserWarning)
                        print(msg)
                        _, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=True)

            self._steppers[num_motor].release()

            pin_value = self.check_pin(pin_value)
            all_pin_value.append(pin_value)

            self._update_move(init_pos - self._antenna_pos[num_motor])

            if pauses:
                pause()

        if plot_pin:
            fig, axs = plt.subplots(len(self._motor_id), figsize=(10, 20))
            for ant, pnv in enumerate(all_pin_value):
                axs[ant].plot(pnv)
                axs[ant].set_title("Antenna: " + str(ant))
            fig.tight_layout(pad=5.0)
            plt.show()

    def move_backward(self, motor, distance, pauses=True, plot_pin=False):
        """Moves motor backward.

        This method moves the specified motor backward (opposite of the
        head) for the specified distance in millimeters. If the distance
        is larger than the maximum distance that the motor can move (
        _DRIVERS_MAX), the motor will move until it reaches the switch and
        then back off until the switch is released.

        If the value of the `motor` parameter is 100, the method moves all
        the motors in the `_steppers` list the same distance.

        Args:
            plot_pin:
            motor (int): The motor number or 100 to move all motors.
            distance (float): The distance in millimeters to move the
            motor backward.
            pauses (bool, optional): Flag indicating whether to pause
            after each motor movement. Defaults to True.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.move_backward(motor=1, distance=10, pauses=True)
            (Motor movement backward is performed)

        Note:
            - The method utilizes the `dist2steps`, `move_switch_off`, `
              check_pin`, `new_position`, and `pause` methods to perform the
              motor movement.
            - The method takes into account the maximum distance that the
              motor can move (_DRIVERS_MAX) and adjusts the distance if it
              exceeds this limit.
            - The method checks the switch status using the GPIO input to
              detect when the motor reaches the switch.
            - After each motor movement, the method checks the pin status
              using the `check_pin` method.
            - The `new_position` method is used to update the motor position
              based on the distance, forward_distance, and the current motor
              position.
            - Pauses after each motor movement can be controlled using the
              `pauses` parameter.
        """
        print("---------------------")
        print("BACKWARD")
        print("---------------------\n")

        start_motor = motor
        end_motor = motor + 1

        if motor == 100:
            start_motor = 0
            end_motor = len(self._steppers)

        all_pin_value = []
        for num_motor in range(start_motor, end_motor):

            pin_value = []
            steps_switch_off = 0

            init_pos = self._antenna_pos[num_motor]

            print("----- Antenna {:d} -----".format(
                self._antenna_number[num_motor]))

            distance_head = distance
            if self._antenna_pos[num_motor] + distance > \
                    _OUTER_DIST[self._antenna_number[num_motor]]:
                print("> Antenna CANNOT MOVE AWAY THAT MUCH, reaching home "
                      "position")

                distance_head = _OUTER_DIST[self._antenna_number[
                    num_motor]] - self._antenna_pos[num_motor]

            print("Moving BACKWARD")
            for _ in range(self._dist2steps(distance_head)):

                self.backward(num_motor)

                pin_value.append(GPIO.input(self._pin_switch))
                if pin_value[-1] == 0:

                    plot_pin = self.plot_pin_states
                    print("Pressed switch")

                    for _ in range(self.pin_checks):
                        extra_steps, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=True)

                        steps_switch_off += extra_steps

                    pin_value.append(GPIO.input(self._pin_switch))
                    if pin_value[-1] == 1:

                        print("Switch released, {:2f} mm needed".format(
                            self._steps2dist(steps_switch_off)))
                        break
                    else:
                        msg = "Unstable Switch State, Repeat Initialization"
                        warnings.warn(msg, UserWarning)
                        print(msg)
                        _, pin_value = self.move_switch_off(
                            num_motor=num_motor, pin_value=pin_value,
                            forward=True)

            self._steppers[num_motor].release()

            pin_value = self.check_pin(pin_value)
            all_pin_value.append(pin_value)

            self._update_move(init_pos - self._antenna_pos[num_motor])

            if pauses:
                pause()

        if plot_pin:
            fig, axs = plt.subplots(len(self._motor_id), figsize=(10, 20))
            for ant, pnv in enumerate(all_pin_value):
                axs[ant].plot(pnv)
                axs[ant].set_title("Antenna: " + str(ant))
            fig.tight_layout(pad=5.0)
            plt.show()

    def create_circle(self, distance_from_head=1, pauses=True):
        """Creates circle that the closest antenna is distance_from_head
            away from the head.

        This method creates a circular shape around the head by moving the
        antennas backward to a specified distance from the head. The circle
        will have a radius equal to the `distance_from_head` parameter in
        millimeters.

        First, each antenna reaches the head and then moves backward
        (diatance_from_head) mm. Second, we find the antenna with the
        maximum distance (diatance = current position +
        distance_from_head) from the center. Finally, we move every
        antenna to the position that matches
        the distance found above.

        Args:
            distance_from_head (float, optional): The radius of the circle.
            Defaults to 1mm.
            pauses (bool, optional): Flag indicating whether to pause after
            each motor movement. Defaults to True.

        Returns:
            None

        Example:
            >>> obj = MotorControl()
            >>> obj.create_circle(distance_from_head=2, pauses=True)
            (Circle movement is performed)

        Note:
            - The method utilizes the `set_on_head`, `move_backward`,
              and `release` methods to create the circle.
            - The `set_on_head` method is called initially to position the
              antennas on the head.
            - The `move_backward` method is used to move each antenna
              backward
              by a distance equal to the difference
              between the target point (calculated based on the maximum
              motor position and `distance_from_head`) and the current
              motor position.
            - The `release` method is called to release the motor after each
              backward movement.
            - If the target point exceeds the maximum limit (_DRIVERS_MAX),
              the method creates the circle with the maximum possible
              radius by setting the target point to _DRIVERS_MAX.
            - Pauses after each motor movement can be controlled using the
              `pauses` parameter.
        """
        print("---------------------")
        print("CIRCLE")
        print("---------------------\n")

        self.set_on_head(pauses=pauses)

        if max(self._antenna_pos) > min(_OUTER_DIST):
            index_max = np.argmax(self._antenna_pos)
            msg = "CANNOT CREATE CIRCLE, Antenna {:d} is further than some " \
                  "antennas can possible reach".format(index_max)
            warnings.warn(msg, UserWarning)
            print(msg)
        else:

            target_point = max(self._antenna_pos) + distance_from_head
            index_max = np.argmax(self._antenna_pos)

            print("MAX DISTANCE is from Antenna {:d}".format(index_max))
            if target_point > min(_OUTER_DIST):
                print('!! Creating Max Circle !!')
                target_point = min(_OUTER_DIST)

            for num_motor in range(len(self._motor_id)):
                self.move_backward(num_motor, target_point - self._antenna_pos[
                    num_motor], pauses=pauses)
                self._steppers[num_motor].release()

    def solve_ellipse_system(self, a, b, c, centroid_x, centroid_y,
                                   num_motor):
        """Solves the ellipse equation system and calculates the coordinates
            and distance for a given antenna.

        This method formulates and solves the ellipse equation system based
        on the provided parameters: `a`, `b`, `c`, `centroid_x`,
        `centroid_y`,
        and `num_motor`. It calculates the coordinates (x, y) and the
        distance from the center for the specified antenna.

        First, we construct the ellipse's and driver's equation.
        After that, we want to find the x, y possible solutions of the 2x2
        system. We expect two solutions. We keep the correct solution based
        on the antenna number.

        Args:
            a (float): Coefficient of the ellipse equation.
            b (float): Coefficient of the ellipse equation.
            c (float): Coefficient of ellipse equation.
            centroid_x (float): X-coordinate of the centroid of the ellipse.
            centroid_y (float): Y-coordinate of the centroid of the ellipse.
            num_motor (int): Antenna number for which to solve the ellipse
            equation system.

        Returns:
            tuple: A tuple containing the calculated x-coordinate,
            y-coordinate, and distance from the center.

        Example:
            >>> obj = MotorControl()
            >>> result = obj.solve_ellipse_system_numpy(a=2.5, b=1.8, c=1.2,
            >>>                                   centroid_x=3.0,
            >>>                                   centroid_y=4.0,
            >>>                                   num_motor=2)
            >>> print(result)
            (2, 0, 2.5)

        Note:
            - The method calculates the ellipse equation using the provided
              coefficients and centroid coordinates.
            - It also calculates the driver equation based on the antenna
              angle obtained from the `get_angle` method.
            - The equation system is solved using the `solve` function from
              `sympy`.
            - The resulting solutions are rounded and used to determine the
              x and y coordinates of the ellipse intersection.
            - The specific x and y values are assigned based on the antenna
              number.
            - The distance from the center is calculated by subtracting the
              inner distance (obtained from `_INNER_DIST`)
              from the Euclidean distance between the x and y coordinates.
        """
        print("Antenna {:d}".format(self._antenna_number[num_motor]))

        tanth = np.tan(np.radians(self.get_angle(num_motor)))
        cp2 = a + 2. * b * tanth + c * tanth * tanth
        cp1 = a * centroid_x + b * (centroid_x * tanth + centroid_y)
        cp1 += c * centroid_y * tanth
        cp1 *= -2.
        cp0 = a * centroid_x * centroid_x
        cp0 += 2. * b * centroid_x * centroid_y
        cp0 += c * centroid_y * centroid_y - 1.

        xsol = np.roots([cp2, cp1, cp0])
        ysol = xsol * tanth

        sol = [(xsol[0], ysol[0]), (xsol[1], ysol[1])]

        if len(sol) == 2:

            if not (isinstance(sol[0][0], complex) or
                    isinstance(sol[1][0], complex) or
                    isinstance(sol[0][1], complex) or
                    isinstance(sol[0][1], complex)):

                x1 = int(round(sol[0][0]))
                y1 = int(round(sol[0][1]))

                x2 = int(round(sol[1][0]))
                y2 = int(round(sol[1][1]))

                if self._antenna_number[num_motor] == 0:
                    x = 0
                    y = y1 if y1 > 0 else y2
                elif self._antenna_number[num_motor] == 1:
                    x = x1 if x1 > 0 else x2
                    y = x
                elif self._antenna_number[num_motor] == 2:
                    x = x1 if x1 > 0 else x2
                    y = 0
                elif self._antenna_number[num_motor] == 3:
                    x = x1 if x1 > 0 else x2
                    y = -x
                elif self._antenna_number[num_motor] == 4:
                    x = 0
                    y = y1 if y1 < 0 else y2
                elif self._antenna_number[num_motor] == 5:
                    x = x1 if x1 < 0 else x2
                    y = x
                elif self._antenna_number[num_motor] == 6:
                    x = x1 if x1 < 0 else x2
                    y = 0
                else:
                    x = x1 if x1 < 0 else x2
                    y = - x

                return x, y, round(np.sqrt(np.square(x) +
                                           np.square(y)) - self._antenna_pos[
                                       num_motor])
            else:
                msg = 'Found Complex Solutions in Equation System'
                warnings.warn(msg, UserWarning)
                print(msg)
                self.__del__()
                sys.exit()
        else:
            msg = 'Number of Solutions in Equation system must be == 2, ' \
                  'found ' + str(len(sol))
            warnings.warn(msg, UserWarning)
            print(msg)
            self.__del__()
            sys.exit()

    def create_ellipse(self, distance_from_head=1, pauses=True, plot=True):
        """This method finds the outer ellipse (around the head) equation
            parameters based on the positions of the antennas.

        We want every antenna to be INSIDE the ellipse!

        It sets the antennas on the head, moves them backward by a specified
        distance, and then calculates the outer ellipse parameters using the
        `outer_ellipsoid_fit` function. It solves the ellipse equation
        system for each antenna to determine the coordinates on the
        ellipse. Finally, it optionally plots the ellipse and antenna
        positions.

        Args:
            distance_from_head (float, optional): Distance from the head to
            create the ellipse (default: 1).
            pauses (bool, optional): Flag indicating whether to pause after
            each step (default: True).
            plot (bool, optional): Flag indicating whether to plot the
            ellipse and antenna positions (default: True).

        Example:
            >>> obj = MotorControl()
            >>> obj.create_ellipse(distance_from_head=2,
            >>>                    pauses=True,
            >>>                    plot=True)

        Note:
            - The method sets the antennas on the head using the
              `set_on_head` method.
            - It then moves the antennas backward by the specified distance
              using the `move_backward` method.
            - If there are only two antenna points, the method exits as it
              cannot compute an ellipse from just two points.
            - For more than two antenna points, the method calculates the
              outer ellipse parameters using `outer_ellipsoid_fit`.
            - The ellipse equation system is solved for each antenna using
              the `solve_ellipse_system` method.
            - The resulting x and y coordinates are stored for each antenna.
            - If the distance from the center plus the current motor
              position exceeds a threshold, a warning message is printed.
            - The antennas are then moved backward to their respective
              ellipse positions.
            - If the move distance is negative, the method exits with an
              error message.
            - If the `plot` flag is set to True, the method calls the
              `plot_ellipse_antennas` method to visualize the ellipse and
              antenna positions.

        Raises:
            SystemExit: If the number of antenna points is less than 3.
        """
        print("> Creating Ellipse...\n\n")
        print("> We set antennas on Head...")

        self.set_on_head(pauses=pauses)

        self.move_backward(motor=100,
                           distance=distance_from_head,
                           pauses=pauses)
        if len(self._motor_id) == 2:
            print("Cannot Compute Ellipse from only 2 points")
        else:
            print("Calculating Outer ellipse")
            a_outer, centroid_outer = outer_ellipsoid_fit(
                np.array(self._antenna_coords))
            a = a_outer[0][0]
            b = a_outer[0][1]
            c = a_outer[1][1]
            c_x = centroid_outer[0]
            c_y = centroid_outer[1]

            if np.square(b) - 4 * a * c >= 0:
                print("Ellipse does NOT correspond to the condition")
                self.__del__()
                sys.exit()

            x_coords = []
            y_coords = []

            for num_motor in range(len(self._motor_id)):
                x, y, distance = self.solve_ellipse_system(a=a,
                                                           b=b,
                                                           c=c,
                                                           centroid_x=c_x,
                                                           centroid_y=c_y,
                                                           num_motor=num_motor)

                x_coords.append(x)
                y_coords.append(y)

                if distance + self._antenna_pos[num_motor] > \
                        _OUTER_DIST[self._antenna_number[num_motor]]:
                    print("We are moving antenna to MAX distance, "
                          "wont correspond to Ellipse equation")
                    distance = \
                        _OUTER_DIST[self._antenna_number[num_motor]] - \
                        self._antenna_pos[num_motor]

                if distance >= 0:

                    self.move_backward(motor=num_motor,
                                       distance=distance,
                                       pauses=pauses)
                elif 0 > distance > -2:

                    self.move_backward(motor=num_motor,
                                       distance=0,
                                       pauses=pauses)
                else:
                    msg = "Cannot move NEGATIVE distance {:2f}".format(distance)
                    warnings.warn(msg, UserWarning)
                    print(msg)
                    self.__del__()
                    sys.exit()
            if plot:
                self.plot_ellipse_antennas(x_coordinates=x_coords,
                                           y_coordinates=y_coords)
