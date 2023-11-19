from plotter import make_plot
from math import sqrt, atan2, cos, sin

# параметры симуляции
MOON_RADIUS = 1
MOON_MASS = 0.5
G = 1

SHIP_MASS = 0.02
ENGINE_WORKING_TIME = 4.5
ENGINE_THRUST = 0.0008
FUEL_MASS0 = 0.01

NEW_VAR = 12
RX0 = 0
RY0 = 1.0
VX0 = 0.7
VY0 = 0.1

COLOR_FUEL = (241,53,53)
COLOR_FREE = (53, 178, 241)
DT = 0.01
SIMULATION_TIME = 40


def distToMoon(x, y):
    return sqrt(x**2 + y**2)


def getAttractionMag(x, y, fullShipMass):
    return G * MOON_MASS * fullShipMass / distToMoon(x, y)**2


def eulerIntegration(rX, rY, vX, vY, fuelMass, fuelFlow):
    fuelMass1 = max(0, fuelMass - fuelFlow * DT)
    fullShipMass = SHIP_MASS + (fuelMass + fuelMass1) / 2

    # сила тяги двигателя
    fEngine = ENGINE_THRUST 
    if (fuelMass + fuelMass1) / 2 <= 0:
        fEngine = 0

    alpha = atan2(vY, vX)

    # сила притяжения
    fAttr = getAttractionMag(rX, rY, fullShipMass)
    phi = atan2(rY, rX)

    aX = (cos(alpha) * fEngine - cos(phi) * fAttr) / fullShipMass
    aY = (sin(alpha) * fEngine - sin(phi) * fAttr) / fullShipMass

    vX1 = vX + aX * DT
    vY1 = vY + aY * DT

    rX1 = rX + (vX + vX1) / 2 * DT
    rY1 = rY + (vY + vY1) / 2 * DT

    return rX1, rY1, vX1, vY1, fuelMass1


def simulation(rX, rY, vX, vY, fuelMass, engineWorkingTime):
    # скорость расхода топлива
    FUEL_FLOW = fuelMass / engineWorkingTime 
    STEPS_COUNT = int(SIMULATION_TIME / DT)

    trajectoryFuel = [(rX, rY)]
    trajectoryFree = []
    isCrash = False

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY, fuelMass = eulerIntegration(rX, rY, vX, vY, fuelMass, FUEL_FLOW)

        if fuelMass > 0:
            trajectoryFuel.append((rX, rY))
        else:
            trajectoryFree.append((rX, rY))
 
        if distToMoon(rX, rY) <= MOON_RADIUS:
            isCrash = True
            break
    
    # соединить траекторию полета с включенным и выключенным двигателем
    trajectoryFree = [trajectoryFuel[-1]] + trajectoryFree

    return trajectoryFuel, trajectoryFree, isCrash


def main(): 
    trajectoryFuel, trajectoryFree, isCrash = simulation(RX0, RY0, VX0, VY0, FUEL_MASS0, ENGINE_WORKING_TIME)

    if isCrash:
        print("CRASH!")

    make_plot(MOON_RADIUS, [
        [COLOR_FUEL, trajectoryFuel],
        [COLOR_FREE, trajectoryFree],
    ], "./model_1/plot.png")


if __name__ == "__main__":
    main()