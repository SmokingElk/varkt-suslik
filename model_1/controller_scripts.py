from controller import ScriptBase
from math import sqrt, pi, atan2
from pid import PidRegulator
from global_params import DT, MOON_RADIUS

SAFE_HEIGHT = 0.1
TARGET_ALPHA = 0.142
INITIAL_ANGLE_ACCURACY = 0.01


def getAngleDifference(alpha, beta):
    phi = abs(alpha - beta)
    sgn = 1 if beta > alpha else -1

    if 2 * pi - phi < phi:
        phi = 2 * pi - phi
        sgn *= -1

    return phi * sgn


class MainScript(ScriptBase):
    def __init__(self):
        self.stage = 0
        self.initialAnglePID = PidRegulator(0, 0, 2, DT)
        self.courseAlignPID = PidRegulator(0, 0, 2, DT)

    def getStage(self):
        return self.stage

    def thrustersControl(self, thrusterLeft, thrusterRight, control):
        thrusterLeft.setThrustLevel(control)
        thrusterRight.setThrustLevel(-control)

    def update(self, model, metrics):
        time = metrics["t"]

        mainEngine = model["main_engine"]
        thrusterLeft = model["thruster_left"]
        thrusterRight = model["thruster_right"]

        alpha = metrics["shipOrientation"]
        theta = atan2(metrics["vY"], metrics["vX"])
        height = sqrt(metrics["rX"]**2 + metrics["rY"]**2) - MOON_RADIUS

        match self.stage:
            case 0:
                mainEngine.active()
                mainEngine.setThrustLevel(1)

                thrusterLeft.active()
                thrusterLeft.setThrustLevel(0)

                thrusterRight.active()
                thrusterRight.setThrustLevel(0)

                print(f"Main engine has been activaited at {time} (stage 1)")
                self.stage = 1
            case 1:
                if height >= SAFE_HEIGHT:
                    print(f"Safe height has been reached at {time} (stage 2)")
                    self.stage = 2
            case 2:
                angleError = getAngleDifference(TARGET_ALPHA, alpha)

                if abs(angleError) < INITIAL_ANGLE_ACCURACY:
                    print(f"Target angle has been reached at {time} (stage 3)")
                    self.stage = 3
                
                controlSignal = self.initialAnglePID.control(angleError)
                self.thrustersControl(thrusterLeft, thrusterRight, controlSignal)
            case 3:
                angleError = getAngleDifference(theta, alpha)

                controlSignal = self.courseAlignPID.control(angleError)
                self.thrustersControl(thrusterLeft, thrusterRight, controlSignal)

                if mainEngine.getFuelMass() <= 0:
                    print(f"Ouf of fuel at {time} (stage 4)")

                    thrusterLeft.inactive()
                    thrusterRight.inactive()

                    self.stage = 4
            case 4:
                pass


if __name__ == "__main__":
    print(getAngleDifference(-pi / 6, pi / 6), pi / 3)