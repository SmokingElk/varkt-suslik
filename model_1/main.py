from plotter import make_plot
from math import sqrt, atan2, cos, sin
from engines import CruiseEngine

# параметры симуляции
# сила притяжения
MOON_RADIUS = 1
MOON_MASS = 0.5
G = 1


CRASH_THRESHOLD = 0.1
SHIP_MASS = 0.02


RX0 = 0
RY0 = 1.0
VX0 = 0.0
VY0 = 0.0

COLOR_FUEL = (241,53,53)
COLOR_FREE = (53, 178, 241)
DT = 0.01
SIMULATION_TIME = 15


def vecMag(x, y):
    return sqrt(x**2 + y**2)


def distToMoon(x, y):
    return vecMag(x, y)


def getAttractionMag(x, y, fullShipMass):
    return G * MOON_MASS * fullShipMass / distToMoon(x, y)**2


def isShipLanded(x, y, vX, vY):
    return distToMoon(x, y) <= MOON_RADIUS and vecMag(vX, vY) < CRASH_THRESHOLD


def eulerIntegration(rX, rY, vX, vY, shipOrientation, engines):
    landed = isShipLanded(rX, rY, vX, vY)
    fullShipMass = SHIP_MASS
    fEngine = 0

    for engine in engines:
        fuelMass = engine.getFuelMass()
        thrust, moment = engine.applyThrust(DT)
        fuelMass1 = engine.getFuelMass()
        fullShipMass += (fuelMass + fuelMass1) / 2
        fEngine += thrust

    # сила притяжения
    fAttr = getAttractionMag(rX, rY, fullShipMass)
    phi = atan2(rY, rX)

    # сила тяги двигателя


    alpha = shipOrientation

    # сила реакции опоры
    fN = fAttr if landed else 0
    
    print(landed, fEngine, fN, fAttr)

    aX = (cos(alpha) * fEngine + cos(phi) * (fN - fAttr)) / fullShipMass
    aY = (sin(alpha) * fEngine + sin(phi) * (fN - fAttr)) / fullShipMass

    vX1 = vX + aX * DT
    vY1 = vY + aY * DT

    rX1 = rX + (vX + vX1) / 2 * DT
    rY1 = rY + (vY + vY1) / 2 * DT

    shipOrientation1 = shipOrientation

    return rX1, rY1, vX1, vY1, shipOrientation1, fEngine


def simulation(rX, rY, vX, vY, engines):
    # скорость расхода топлива

    STEPS_COUNT = int(SIMULATION_TIME / DT)

    shipOrientation = atan2(rY, rX)

    trajectoryFuel = [(rX, rY)]
    trajectoryFree = []
    isCrash = False

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY, shipOrientation, engineForces = eulerIntegration(rX, rY, vX, vY, shipOrientation, engines)

        if engineForces > 0:
            trajectoryFuel.append((rX, rY))
        else:
            trajectoryFree.append((rX, rY))
 
        if distToMoon(rX, rY) <= MOON_RADIUS and not isShipLanded(rX, rY, vX, vY):
            print(vecMag(vX, vY), distToMoon(rX, rY) <= MOON_RADIUS)
            isCrash = True
            break
    
    # соединить траекторию полета с включенным и выключенным двигателем
    trajectoryFree = [trajectoryFuel[-1]] + trajectoryFree

    return trajectoryFuel, trajectoryFree, isCrash


def main():
    ENGINE_WORKING_TIME = 4.5
    ENGINE_THRUST = 0.015
    FUEL_MASS0 = 0.01

    main_engine = CruiseEngine(ENGINE_THRUST, FUEL_MASS0, ENGINE_WORKING_TIME)

    main_engine.active()
    engines = [main_engine]
    trajectoryFuel, trajectoryFree, isCrash = simulation(RX0, RY0, VX0, VY0, engines)

    if isCrash:
        print("CRASH!")

    make_plot(MOON_RADIUS, [
        [COLOR_FUEL, trajectoryFuel],
        [COLOR_FREE, trajectoryFree],
    ], "plot.png")


if __name__ == "__main__":
    main()