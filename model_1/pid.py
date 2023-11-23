class PidRegulator:
    def __init__(self, kP, kI, kD, dt):
        self.kP = kP
        self.kI = kI
        self.kD = kD
        self.dt = dt

    def reset(self):
        self.prevErr = 0
        self.errIntegral = 0

    def control(self, err):
        dErr = err - self.prevErr
        self.prevErr = err

        self.errIntegral += dErr * self.dt
        dErrDt = dErr / self.dt

        return self.kP * err + self.kI * self.errIntegral + self.kD * dErrDt