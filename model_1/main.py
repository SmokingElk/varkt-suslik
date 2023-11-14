from plotter import make_plot
from math import sqrt, atan2, cos, sin

MOON_RADIUS = 1
MOON_MASS = 0.5
SHIP_MASS = 0.02
G = 1

COLOR = (53, 178, 241)
DT = 0.01
STEPS_COUNT = 8000

RX0 = 0
RY0 = 1.2

VX0 = 0.8
VY0 = 0.0


def distToMoon(x, y):
    return sqrt(x**2 + y**2)


def getAttractionMag(x, y):
    return G * MOON_MASS * SHIP_MASS / distToMoon(x, y)**2


def eulerIntegration(rX, rY, vX, vY):
    fAttr = getAttractionMag(rX, rY)
    phi = atan2(rY, rX)

    aX = -cos(phi) * fAttr / SHIP_MASS
    aY = -sin(phi) * fAttr / SHIP_MASS

    vX1 = vX + aX * DT
    vY1 = vY + aY * DT

    rX1 = rX + (vX + vX1) / 2 * DT
    rY1 = rY + (vY + vY1) / 2 * DT

    return rX1, rY1, vX1, vY1


def simulation(rX, rY, vX, vY):
    trajectory = [(rX, rY)]
    isCrash = False

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY = eulerIntegration(rX, rY, vX, vY)

        trajectory.append((rX, rY))

        isCrash = distToMoon(rX, rY) <= MOON_RADIUS
        if isCrash:
            break

    return trajectory, isCrash


def main(): 
    trajectory, isCrash = simulation(RX0, RY0, VX0, VY0)

    if isCrash:
        print("CRASH!")

    make_plot(MOON_RADIUS, [
        [COLOR, trajectory],
    ], "./model_1/plot.png")


if __name__ == "__main__":
    main()