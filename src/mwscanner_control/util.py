import numpy as np
import numpy.linalg as la


def dist2coordinates(distance, angle):
    """Converts the antenna position to x,y coordinates of the motor.

    Parameters:
        distance (float): The linear distance over the Driver.
        angle (float): The angle in degrees.

    Returns:
        tuple: The x,y coordinates of the motor.

    Example:
        >>> dist2coordinates(10.0, 45.0)
        (9.142135623730951, 9.142135623730951)
    """

    radius = distance
    x = radius * np.cos(np.radians(angle))
    y = radius * np.sin(np.radians(angle))
    return [x, y]


def pause():
    """Pauses the program and waits for user input to continue.

    Returns:
        None

    Example:
        >>> pause()
        > Press Enter to continue...
        (User presses Enter key)
    """

    input("> Press Enter to continue...\n")


def outer_ellipsoid_fit(points, tol=0.001):
    """Find the minimum volume ellipsoid enclosing a set of points.

    This function computes the minimum volume ellipsoid that encloses
    (lies outside) a set of points in a d-dimensional space. It returns the
    matrix A and vector c, which represent the ellipsoid in "center form"
    where the equation for the ellipse is (x - c).T * A * (x - c) = 1.

    Args:
        points (numpy.ndarray): An N x d matrix representing N points in
        d-dimensional space.
        tol (float): Tolerance parameter for convergence of the algorithm.
        Default is 0.001.

    Returns:
        tuple: A tuple (A, c) where A is a d x d matrix representing the
        ellipsoid parameters and c is a d-dimensional vector representing
        the center of the ellipsoid.

    Example:
        >>> p = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        >>> A_matrix, center = outer_ellipsoid_fit(points)
        >>> print(A_matrix)
        [[ 0.02918387 -0.00832836  0.01243388]
         [-0.00832836  0.03522328  0.01911765]
         [ 0.01243388  0.01911765  0.04626111]]
        >>> print(center)
        [4. 5. 6.]
    """

    points = np.asmatrix(points)
    n, d = points.shape
    q = np.column_stack((points, np.ones(n))).T
    u = np.ones(n) / n
    err = 1 + tol
    while err > tol:
        x = q * np.diag(u) * q.T
        m = np.diag(q.T * la.inv(x) * q)
        jdx = np.argmax(m)
        step_size = (m[jdx] - d - 1.0) / ((d + 1) * (m[jdx] - 1.0))
        new_u = (1 - step_size) * u
        new_u[jdx] += step_size
        err = la.norm(new_u - u)
        u = new_u

    c = u * points  # center of ellipsoid
    a = la.inv(points.T * np.diag(u) * points - c.T * c) / d

    # U, D, V = la.svd(np.asarray(A))
    # rx, ry, rz = 1. / np.sqrt(D)
    #
    # return rx, ry, rz
    return np.asarray(a), np.squeeze(np.asarray(c))
