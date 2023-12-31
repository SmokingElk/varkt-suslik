from plotter import makeOrbitPlot
from math import sqrt, atan2, cos, sin, pi
from rocket_parts import Part, getInertiaMoment
from engines import CruiseEngine, ManeuveringThruster
from controller import Controller
from controller_scripts import MainScriptV1, MainScriptV2
from global_params import RX0, RY0, VX0, VY0, CRASH_THRESHOLD, MOON_RADIUS, MOON_MASS, G, DT, SIMULATION_TIME, MAX_ORBIT_HEIGHT, TIME_MASS_FACTOR, MAIN_ENGINE_MASS, MAIN_ENGINE_THRUST, MAIN_ENGINE_HEIGHT, PAYLOAD_HEIGHT, THRUSTERS_HEIGHT, THRUSTERS_THRUST

COLORS = [
    (241, 53, 228),
    (241, 207, 53),
    (241, 53, 53),
    (53, 147, 241),
    (0, 197, 95),
]

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
    shipAngularVel1 = shipAngularVel + shipAngularAcc * DT
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


def updateOrbitStatistics(rX, rY, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist):
    distToSurface = distToMoon(rX, rY) - MOON_RADIUS

    apocenterPoint1 = apocenterPoint
    apocenterDist1 = apocenterDist
    pericenterPoint1 = pericenterPoint
    pericenterDist1 = pericenterDist

    if distToSurface > apocenterDist:
        apocenterDist1 = distToSurface
        apocenterPoint1 = (rX, rY)

    if distToSurface < pericenterDist:
        pericenterDist1 = distToSurface
        pericenterPoint1 = (rX, rY)

    return apocenterPoint1, apocenterDist1, pericenterPoint1, pericenterDist1


def simulation(rX, rY, vX, vY, engines, parts, needLog, autopilot):
    STEPS_COUNT = int(SIMULATION_TIME / DT)
    mainScript = MainScriptV1() if autopilot == "V1" else MainScriptV2()
    
    controller = Controller({
        "main_engine": engines[0], 
        "thruster_left": engines[1], 
        "thruster_right": engines[2],
        "parts": parts,
    }, [mainScript], needLog)

    shipOrientation = atan2(rY, rX)
    shipAngularVel = 0

    trajectories = [[(rX, rY)]]
    isCrash = False

    apocenterPoint = (0, 0)
    apocenterDist = 0
    pericenterPoint = (0, 0)
    pericenterDist = MAX_ORBIT_HEIGHT

    for i in range(STEPS_COUNT):
        rX, rY, vX, vY, shipOrientation, shipAngularVel = eulerIntegration(rX, rY, vX, vY, shipOrientation, shipAngularVel, engines, parts)

        if mainScript.getStage() < len(trajectories):
            trajectories[-1].append((rX, rY))
        else:
            lastPoint = trajectories[-1][-1]
            trajectories.append([lastPoint, (rX, rY)])

        controller.update(t=i * DT, rX=rX, rY=rY, vX=vX, vY=vY, shipOrientation=shipOrientation, shipAngularVel=shipAngularVel)
        if mainScript.isFreeFlight():
            apocenterPoint, apocenterDist, pericenterPoint, pericenterDist = updateOrbitStatistics(rX, rY, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist)

        if distToMoon(rX, rY) <= MOON_RADIUS and not isShipLanded(rX, rY, vX, vY):
            isCrash = True
            break

    orbitWasReached = (not isCrash) and (MOON_RADIUS + apocenterDist <= MAX_ORBIT_HEIGHT)

    return trajectories, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist, isCrash, orbitWasReached


def calculateOrbitData(fuelMass, payloadMass, needLog=False, autopilot="V1"):
    mainEngine = CruiseEngine(
        thrust=MAIN_ENGINE_THRUST, 
        fuelMass0=fuelMass, 
        workingTime=TIME_MASS_FACTOR * fuelMass, 
        height=MAIN_ENGINE_HEIGHT, 
        mass=MAIN_ENGINE_MASS,
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
    parts = [mainEngine, Part(payloadMass, PAYLOAD_HEIGHT)]

    return simulation(RX0, RY0, VX0, VY0, engines, parts, needLog, autopilot)


def colorizeTrajectories(trajectories, colors):
    return [[colors[i % len(colors)], trajectories[i]] for i in range(len(trajectories))]


def main():
    fuelMass = 6.5 * 10**3
    payloadMass = 3.5 * 10**3

    trajectories, apocenterPoint, apocenterDist, pericenterPoint, pericenterDist, isCrash, orbitWasReached = calculateOrbitData(fuelMass, payloadMass, True, autopilot="V2")

    if isCrash:
        print("CRASH!")

    if orbitWasReached:
        print(f"Apocenter distance: {apocenterDist}")
        print(f"Pericenter distance: {pericenterDist}")
    else:
        print("Orbit wasn't reached.")

    makeOrbitPlot(
        MOON_RADIUS, 
        apocenterPoint,
        apocenterDist,
        pericenterPoint,
        pericenterDist,
        orbitWasReached,
        colorizeTrajectories(trajectories, COLORS), 
        "./model_1/plot.png"
    )


if __name__ == "__main__":
    main()