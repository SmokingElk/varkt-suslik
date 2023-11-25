from plotter import make_plot
from math import sqrt, atan2, cos, sin, pi
from rocket_parts import Part, getInertiaMoment
from engines import CruiseEngine, ManeuveringThruster
from controller import Controller
from controller_scripts import MainScript
from global_params import RX0, RY0, VX0, VY0, CRASH_THRESHOLD, MOON_RADIUS, MOON_MASS, G, DT, SIMULATION_TIME

COLOR_FUEL = (241,53,53)
COLOR_FREE = (53, 178, 241)

PI_2 = 2 * pi


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

    # сила притяжения
    fAttr = getAttractionMag(rX, rY, fullShipMass)
    phi = atan2(rY, rX)

    # сила реакции опоры
    fN = fAttr if landed else 0

    # интегрирование ориентации и угловой скорости
    inertiaMoment = getInertiaMoment(parts)

    shipAngularAcc = momentsSum / inertiaMoment
    shipAngularVel1 = (shipAngularVel + shipAngularAcc * DT + PI_2) % PI_2 
    shipOrientation1 = (shipOrientation + (shipAngularVel + shipAngularVel1) / 2 * DT + PI_2) % PI_2
    
    # направление корабля
    alpha = shipOrientation1

    # интегрирование позиции и скорости
    aX = (cos(alpha) * fEngine + cos(phi) * (fN - fAttr)) / fullShipMass
    aY = (sin(alpha) * fEngine + sin(phi) * (fN - fAttr)) / fullShipMass

    vX1 = vX + aX * DT
    vY1 = vY + aY * DT

    rX1 = rX + (vX + vX1) / 2 * DT
    rY1 = rY + (vY + vY1) / 2 * DT

    return rX1, rY1, vX1, vY1, shipOrientation1, shipAngularVel1

def simulation(rX, rY, vX, vY, engines, parts):
    STEPS_COUNT = int(SIMULATION_TIME / DT)
    controller = Controller({"main_engine": engines[0], "thruster_left": engines[1], "thruster_right": engines[2]}, [MainScript()])

    shipOrientation = atan2(rY, rX)
    shipAngularVel = 0

    trajectoryFuel = [(rX, rY)]
    trajectoryFree = []
    isCrash = False

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY, shipOrientation, shipAngularVel = eulerIntegration(rX, rY, vX, vY, shipOrientation, shipAngularVel, engines, parts)
        
        controller.update(t=i * DT, rX=rX, rY=rY, vX=vX, vY=vY, shipOrientation=shipOrientation, shipAngularVel=shipAngularVel)
        
        if engines[0].isActive():
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
    THRUSTERS_HEIGHT = 0.00000009
    THRUSTERS_THRUST = 0.00001

    mainEngine = CruiseEngine(
        thrust=0.015, 
        fuelMass0=0.01, 
        workingTime=4.5, 
        height=0.00003, 
        mass=0.015
    )

    thrusterRight = ManeuveringThruster(
        thrust=THRUSTERS_THRUST, 
        height=THRUSTERS_HEIGHT, 
        direction=-1
    )

    thrusterLeft = ManeuveringThruster(
        thrust=THRUSTERS_THRUST, 
        height=THRUSTERS_HEIGHT, 
        direction=1
    )

    engines = [mainEngine, thrusterLeft, thrusterRight]
    parts = [mainEngine, Part(0.005, 0.00004)]

    trajectoryFuel, trajectoryFree, isCrash = simulation(RX0, RY0, VX0, VY0, engines, parts)

    if isCrash:
        print("CRASH!")

    make_plot(MOON_RADIUS, [
        [COLOR_FUEL, trajectoryFuel],
        [COLOR_FREE, trajectoryFree],
    ], "./model_1/plot.png")


if __name__ == "__main__":
    main()