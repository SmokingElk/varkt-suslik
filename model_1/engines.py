class EngineBase:
    def __init__(self, thrust):
        self._thrust = thrust
        self._isActive = False

    def active(self):
        self._isActive = True

    def inactive(self):
        self._isActive = False

    def isActive(self):
        return self._isActive

    def getThrust(self):
        return self._thrust if self.isActive() else 0
    
    def applyThrust(self, dt):
        return self.getThrust(), 0
    

class CruiseEngine(EngineBase):
    def __init__(self, thrust, fuelMass0, workingTime):
        super().__init__(thrust)

        self._fuelMass = fuelMass0
        self._dFuelMassDt = fuelMass0 / workingTime
        self._workingTime = workingTime

    def getFuelMassDt(self):
        return self._dFuelMassDt

    def getFuelMass(self):
        return self._fuelMass

    def active(self):
        if self.getFuelMass() > 0:
            super().active()

    def applyThrust(self, dt):
        self._fuelMass = max(0, self.getFuelMass() - self.getDFuelMassDt() * dt)

        if self.getFuelMass() <= 0:
            self.inactive()

        return super().applyThrust()
    

class ManeuveringThruster(EngineBase):
    # direction:
    # 1 - cw
    # -1 - ccw
    def __init__(self, thrust, height, direction):
        super().__init__(thrust)

        self._height = height
        self._direction = direction

    def getMoment(self):
        return self._height * self._direction * self.getThrust() 

    def applyThrust(self, dt):
        return 0, self.getMoment()