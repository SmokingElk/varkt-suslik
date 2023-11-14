from plotter import make_plot
from math import sqrt, atan2, cos, sin

# параметры симуляции
MOON_RADIUS = 1
MOON_MASS = 0.5
G = 1

SHIP_MASS = 0.02
ENGINE_WORKING_TIME = 0.03
ENGINE_FORCE_MAG = 0.02
FUEL_MASS0 = 0.0

RX0 = 0
RY0 = 1.0
VX0 = 0.1
VY0 = 0.1

COLOR = (53, 178, 241)
DT = 0.01
STEPS_COUNT = 8000


def distToMoon(x, y):
    return sqrt(x**2 + y**2)


def getAttractionMag(x, y):
    return G * MOON_MASS * SHIP_MASS / distToMoon(x, y)**2


def eulerIntegration(rX, rY, vX, vY, fuelMass, fuelFlow):
    fuelMass1 = max(0, fuelMass - fuelFlow * DT)
    fullShipMass = SHIP_MASS + (fuelMass + fuelMass1) / 2

    fEngine = ENGINE_FORCE_MAG 
    if (fuelMass + fuelMass1) / 2 > 0:
        fEngine = 0
    alpha = atan2(vY, vX)

    fAttr = getAttractionMag(rX, rY)
    phi = atan2(rY, rX)

    aX = (cos(alpha) * fEngine - cos(phi) * fAttr) / fullShipMass
    aY = (sin(alpha) * fEngine - sin(phi) * fAttr) / fullShipMass

    vX1 = vX + aX * DT
    vY1 = vY + aY * DT

    rX1 = rX + (vX + vX1) / 2 * DT
    rY1 = rY + (vY + vY1) / 2 * DT

    return rX1, rY1, vX1, vY1, fuelMass1


def simulation(rX, rY, vX, vY, fuelMass, engineWorkingTime):
    FUEL_FLOW = fuelMass / engineWorkingTime # удельный расход топлива
    
    trajectory = [(rX, rY)]
    isCrash = False

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY, fuelMass = eulerIntegration(rX, rY, vX, vY, fuelMass, FUEL_FLOW)

        trajectory.append((rX, rY))

        isCrash = distToMoon(rX, rY) <= MOON_RADIUS
        if isCrash:
            break

    return trajectory, isCrash


def main(): 
    trajectory, isCrash = simulation(RX0, RY0, VX0, VY0, FUEL_MASS0, ENGINE_WORKING_TIME)

    if isCrash:
        print("CRASH!")

    make_plot(MOON_RADIUS, [
        [COLOR, trajectory],
    ], "./model_1/plot.png")


if __name__ == "__main__":
    main()