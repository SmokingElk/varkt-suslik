from controller import ScriptBase
from math import sqrt, pi, atan2, acos
from pid import PidRegulator
from global_params import DT, MOON_RADIUS, MOON_MASS, G

SAFE_HEIGHT = 0.1
TARGET_ALPHA = -pi / 3
INITIAL_ANGLE_ACCURACY = 0.01
VELOCITY_ALIGNING_DELAY = 0.5

def getAngleDifference(alpha, beta):
    phi = abs(alpha - beta)
    sgn = 1 if beta > alpha else -1

    if 2 * pi - phi < phi:
        phi = 2 * pi - phi
        sgn *= -1

    return phi * sgn


class MainScriptBase(ScriptBase):
    def __init__(self):
        super().__init__()

        self.stage = 0
        self._isFreeFlight = False

    def isFreeFlight(self):
        return self._isFreeFlight

    def getStage(self):
        return self.stage

    def thrustersControl(self, thrusterLeft, thrusterRight, control):
        thrusterLeft.setThrustLevel(control)
        thrusterRight.setThrustLevel(-control)

    def update(self, model, metrics):
        return super().update(model, metrics)


class MainScriptV1(MainScriptBase):
    def __init__(self):
        super().__init__()

        self.initialAnglePID = PidRegulator(4, 0, 2, DT)

    def update(self, model, metrics, log):
        time = metrics["t"]

        mainEngine = model["main_engine"]
        thrusterLeft = model["thruster_left"]
        thrusterRight = model["thruster_right"]

        alpha = metrics["shipOrientation"]
        height = sqrt(metrics["rX"]**2 + metrics["rY"]**2) - MOON_RADIUS

        match self.stage:
            case 0:
                mainEngine.active()
                mainEngine.setThrustLevel(1)

                thrusterLeft.active()
                thrusterLeft.setThrustLevel(0)

                thrusterRight.active()
                thrusterRight.setThrustLevel(0)

                log(f"Main engine has been activaited at {time} (stage 1)")
                self.stage = 1
            case 1:
                if height >= SAFE_HEIGHT:
                    log(f"Safe height has been reached at {time} (stage 2)")
                    self.stage = 2
            case 2:
                angleError = getAngleDifference(alpha, TARGET_ALPHA)

                if abs(angleError) < INITIAL_ANGLE_ACCURACY:
                    log(f"Target angle has been reached at {time} (stage 3)")
                    self.stage = 3
                    mainEngine.setThrustLevel(0)
                    self._isFreeFlight = True
                
                controlSignal = self.initialAnglePID.control(angleError)
                self.thrustersControl(thrusterLeft, thrusterRight, controlSignal)
                
            case 3:
                self.thrustersControl(thrusterLeft, thrusterRight, 0)
                pass


class MainScriptV2(MainScriptBase):
    def __init__(self):
        super().__init__()

        self.initialAnglePID = PidRegulator(64, 0, 2, DT)

    def update(self, model, metrics, log):
        time = metrics["t"]

        mainEngine = model["main_engine"]
        thrusterLeft = model["thruster_left"]
        thrusterRight = model["thruster_right"]

        alpha = metrics["shipOrientation"]
        distToMoon = sqrt(metrics["rX"]**2 + metrics["rY"]**2)
        height = distToMoon - MOON_RADIUS

        targetAlpha = atan2(-metrics["rX"] / distToMoon, metrics["rY"] / distToMoon)

        match self.stage:
            case 0:
                mainEngine.active()
                mainEngine.setThrustLevel(1)

                thrusterLeft.active()
                thrusterLeft.setThrustLevel(0)

                thrusterRight.active()
                thrusterRight.setThrustLevel(0)

                log(f"Main engine has been activaited at {time} (stage 1)")
                self.stage = 1
            case 1:
                if height >= SAFE_HEIGHT:
                    log(f"Safe height has been reached at {time} (stage 2)")
                    self.stage = 2
            case 2:
                angleError = getAngleDifference(alpha, targetAlpha)

                if mainEngine.getFuelMass() <= 0:
                    log(f"Out of fuel at {time} (stage 3)")
                    self.stage = 3
                    mainEngine.setThrustLevel(0)
                    self._isFreeFlight = True
                
                controlSignal = self.initialAnglePID.control(angleError)
                self.thrustersControl(thrusterLeft, thrusterRight, controlSignal)
                
            case 3:
                self.thrustersControl(thrusterLeft, thrusterRight, 0)
                pass


'''
class MainScriptV3(MainScriptBase):
    def __init__(self):
        super().__init__()

        self.initialAnglePID = PidRegulator(64, 0, 2, DT)

    def update(self, model, metrics, log):
        time = metrics["t"]

        mainEngine = model["main_engine"]
        thrusterLeft = model["thruster_left"]
        thrusterRight = model["thruster_right"]

        alpha = metrics["shipOrientation"]
        phi = atan2(metrics["rY"], metrics["rX"])

        distToMoon = sqrt(metrics["rX"]**2 + metrics["rY"]**2)
        height = distToMoon - MOON_RADIUS

        mainEngineThrust = mainEngine.getThrust() * mainEngine.getThrustLevel()

        fullShipMass = sum([i.getMass() for i in model["parts"]])
        fAttr = G * MOON_MASS * fullShipMass / (distToMoon**2)
        theta = acos(fAttr / mainEngine.get)

        targetAlpha = atan2(-metrics["rX"] / distToMoon, metrics["rY"] / distToMoon)

        match self.stage:
            case 0:
                mainEngine.active()
                mainEngine.setThrustLevel(1)

                thrusterLeft.active()
                thrusterLeft.setThrustLevel(0)

                thrusterRight.active()
                thrusterRight.setThrustLevel(0)

                log(f"Main engine has been activaited at {time} (stage 1)")
                self.stage = 1
            case 1:
                if height >= SAFE_HEIGHT:
                    log(f"Safe height has been reached at {time} (stage 2)")
                    self.stage = 2
            case 2:
                angleError = getAngleDifference(alpha, targetAlpha)

                if mainEngine.getFuelMass() <= 0:
                    log(f"Out of fuel at {time} (stage 3)")
                    self.stage = 3
                    mainEngine.setThrustLevel(0)
                    self._isFreeFlight = True
                
                controlSignal = self.initialAnglePID.control(angleError)
                self.thrustersControl(thrusterLeft, thrusterRight, controlSignal)
                
            case 3:
                self.thrustersControl(thrusterLeft, thrusterRight, 0)
                pass
'''
                
if __name__ == "__main__":
    print(getAngleDifference(1.5708, 0.142))