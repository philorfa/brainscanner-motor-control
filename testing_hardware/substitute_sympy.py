import numpy as np
from sympy import solve, var
import time


_ANGLES = [90, 45, 0, 315, 270, 225, 180, 135]


def get_angle(motor_num):
    return _ANGLES[motor_num]


# sympy code
def solve_ell_sympy(a, b, c, centroid_x, centroid_y, num_motor):
    # print("Antenna {:d}".format(num_motor))

    xi = var('x', real=True)
    psi = var('y', real=True)

    equation_ellipse = a * np.square(xi - centroid_x) + 2 * b * (
            xi - centroid_x) * (
                                psi - centroid_y) + c * np.square(
        psi - centroid_y) - 1

    equation_driver = psi * np.cos(
        np.radians(get_angle(num_motor))) - xi * np.sin(
        np.radians(get_angle(num_motor)))

    sol = solve([equation_ellipse, equation_driver], xi, psi, dict=True)
    return sol


def solve_ell_numpy(a, b, c, centroid_x, centroid_y, num_motor):
    tanth = np.tan(np.radians(get_angle(num_motor)))
    cp2 = a + 2. * b * tanth + c * tanth * tanth
    cp1 = a * centroid_x + b * (centroid_x * tanth + centroid_y)
    cp1 += c * centroid_y * tanth
    cp1 *= -2.
    cp0 = a * centroid_x * centroid_x
    cp0 += 2. * b * centroid_x * centroid_y
    cp0 += c * centroid_y * centroid_y - 1.

    xsol = np.roots([cp2, cp1, cp0])
    ysol = xsol * tanth
    return [(xsol[0], ysol[0]), (xsol[1], ysol[1])]


aval = 2.5
bval = 1.8
cval = 1.2
cntx = 3.0
cnty = 4.0
num_motor = 2

start_time = time.time()
for _ in range(12):
    sol1 = solve_ell_sympy(a=aval, b=bval, c=cval, centroid_x=cntx,
                           centroid_y=cnty, num_motor=num_motor)
print("Sympy", time.time() - start_time)

start_time = time.time()
for _ in range(12):
    sol2 = solve_ell_numpy(a=aval, b=bval, c=cval, centroid_x=cntx,
                           centroid_y=cnty, num_motor=num_motor)
print("Nympy", time.time() - start_time)

print(len(sol1))
print(len(sol2))
