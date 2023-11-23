class PidRegulator:
    def __init__(self, kP, kI, kD, dt):
        self.kP = kP
        self.kI = kI
        self.kD = kD
        self.dt = dt

        self.reset()

    def reset(self):
        self.prevErr = 0
        self.errIntegral = 0

    def control(self, err):
        dErr = err - self.prevErr
        self.prevErr = err

        self.errIntegral += dErr * self.dt
        dErrDt = dErr / self.dt

        return self.kP * err + self.kI * self.errIntegral + self.kD * dErrDt
    

if __name__ == "__main__":
    from time import sleep
    from math import sin

    DT = 0.1
    pid = PidRegulator(0.0001, 0.0001, 0.99, DT)

    current = 0
    v = 0
    target = 20
    t = 0

    while True:
        sleep(DT)
        
        target = 20 + 2 * sin(t / 10)
        v += pid.control(target - current) * DT
        current += v * DT
        t += DT
        print(f"{current:.10f} {target:.10f} {abs(target - current):.10f}")