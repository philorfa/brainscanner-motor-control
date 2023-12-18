NUM_CONTROLS = 17

# Max distance the motor can cover with the current hardware (in mm)
# Antenna = [0, 1, 2, 3, 4, 5, 6, 7]
DRIVERS_MAX = [40, 40, 40, 40, 40, 40, 40, 40]


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
OUT_DIST04 = 221

# 1-5: 204
OUT_DIST15 = 204

# 2-6: 204
OUT_DIST26 = 204

# 3-7: 200
OUT_DIST37 = 200

# Distance of each antenna from the center (in mm) in home position
OUTER_DIST = [OUT_DIST04/2, OUT_DIST15/2, OUT_DIST26/2, OUT_DIST37/2,
              OUT_DIST04/2, OUT_DIST15/2, OUT_DIST26/2, OUT_DIST37/2]

# MAX distance allowed of each antenna from the center (in mm) in close position
INNER_DIST = [OUTER_DIST[0] - DRIVERS_MAX[0],
              OUTER_DIST[1] - DRIVERS_MAX[1],
              OUTER_DIST[2] - DRIVERS_MAX[2],
              OUTER_DIST[3] - DRIVERS_MAX[3],
              OUTER_DIST[4] - DRIVERS_MAX[4],
              OUTER_DIST[5] - DRIVERS_MAX[5],
              OUTER_DIST[6] - DRIVERS_MAX[6],
              OUTER_DIST[7] - DRIVERS_MAX[7]]

# Angle of each antenna (in degrees)
# Antenna = [0, 1, 2, 3, 4, 5, 6, 7]
ANGLES = [90, 45, 0, 315, 270, 225, 180, 135]
