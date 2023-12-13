from math import pi

# сила притяжения
MOON_RADIUS = 2 * 10**5
MOON_MASS = 9.76 * 10**20
G = 6.674 * 10**(-11)

DRY_MASS = 3.165 * 10**3

# характеристики двигателя
MAIN_ENGINE_MASS = 0.7 * DRY_MASS 
MAIN_ENGINE_THRUST = 6 * 10**4
MAIN_ENGINE_HEIGHT = 6
TIME_MASS_FACTOR = 135 / (3.4 * 10**3)

THRUSTERS_HEIGHT = 0.18
THRUSTERS_THRUST = 40

PAYLOAD_HEIGHT = 8

# кинематические характеристики ракеты
RX0 = 0
RY0 = MOON_RADIUS
VX0 = 0.0
VY0 = 0.0

# параметры сценария вывода на орбиту
SAFE_HEIGHT = 0.1 * MOON_RADIUS
TARGET_ALPHA = -pi / 3
INITIAL_ANGLE_ACCURACY = 0.01

# параметры симуляции
CRASH_THRESHOLD = 0.1
MAX_ORBIT_HEIGHT = MOON_RADIUS * 5
DT = 1
SIMULATION_TIME = 958 * 11