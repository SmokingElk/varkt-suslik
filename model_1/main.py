from plotter import make_plot
from math import sqrt, atan2, cos, sin
from rocket_parts import Part, getInertiaMoment
from engines import CruiseEngine, ManeuveringThruster

# параметры симуляции
# сила притяжения
MOON_RADIUS = 1
MOON_MASS = 0.5
G = 1

CRASH_THRESHOLD = 0.1

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


def eulerIntegration(rX, rY, vX, vY, shipOrientation, shipAngularVel, engines, parts):
    landed = isShipLanded(rX, rY, vX, vY)
    fullShipMass = sum([i.getMass() for i in parts])
    fEngine = 0

    momentsSum = 0

    for engine in engines:
        thrust, moment = engine.applyThrust(DT)
        fEngine += thrust
        momentsSum += moment

    # вращение
    inertiaMoment = getInertiaMoment(parts)

    shipAngularAcc = momentsSum / inertiaMoment
    shipAngularVel1 = shipAngularVel + shipAngularAcc * DT
    shipOrientation1 = shipOrientation + (shipAngularVel + shipAngularVel1) / 2 * DT

    # сила притяжения
    fAttr = getAttractionMag(rX, rY, fullShipMass)
    phi = atan2(rY, rX)

    # сила реакции опоры
    fN = fAttr if landed else 0
    
    # сила тяги двигателя
    alpha = (shipOrientation + shipOrientation1) / 2

    # сила реакции опоры
    fN = fAttr if landed else 0
    
    print(inertiaMoment, momentsSum, shipAngularAcc)

    aX = (cos(alpha) * fEngine + cos(phi) * (fN - fAttr)) / fullShipMass
    aY = (sin(alpha) * fEngine + sin(phi) * (fN - fAttr)) / fullShipMass

    vX1 = vX + aX * DT
    vY1 = vY + aY * DT

    rX1 = rX + (vX + vX1) / 2 * DT
    rY1 = rY + (vY + vY1) / 2 * DT

    return rX1, rY1, vX1, vY1, shipOrientation1, shipAngularVel1, fEngine

  
def simulation(rX, rY, vX, vY, engines, parts):
    STEPS_COUNT = int(SIMULATION_TIME / DT)

    shipOrientation = atan2(rY, rX)
    shipAngularVel = 0

    trajectoryFuel = [(rX, rY)]
    trajectoryFree = []
    isCrash = False

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY, shipOrientation, shipAngularVel, engineForces = eulerIntegration(rX, rY, vX, vY, shipOrientation, shipAngularVel, engines, parts)

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
    ENGINE_WORKING_TIME = 4
    ENGINE_THRUST = 0.015
    FUEL_MASS0 = 0.01
    ENGINE_HEIGHT = 0.00003
    ENGINE_MASS = 0.015

    main_engine = CruiseEngine(
        ENGINE_THRUST, 
        FUEL_MASS0, 
        ENGINE_WORKING_TIME, 
        ENGINE_HEIGHT, 
        ENGINE_MASS
    )

    main_engine.active()

    thrusterRight = ManeuveringThruster(0.00001, 0.000000016, 1)
    thrusterRight.active()
    thrusterRight.setThrustLevel(1)

    engines = [main_engine, thrusterRight]
    parts = [main_engine, Part(0.005, 0.00004)]
    trajectoryFuel, trajectoryFree, isCrash = simulation(RX0, RY0, VX0, VY0, engines, parts)

    if isCrash:
        print("CRASH!")

    make_plot(MOON_RADIUS, [
        [COLOR_FUEL, trajectoryFuel],
        [COLOR_FREE, trajectoryFree],
    ], "./model_1/plot.png")


if __name__ == "__main__":
    main()