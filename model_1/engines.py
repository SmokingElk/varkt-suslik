from rocket_parts import Part


class EngineBase(Part):
    def __init__(self, thrust, mass=0, height=0):
        super().__init__(mass, height)
        self._thrust = thrust
        self._isActive = False
        self._thrustLevel = 1

    def active(self):
        self._isActive = True

    def inactive(self):
        self._isActive = False

    def isActive(self):
        return self._isActive

    def getThrust(self):
        return self._thrust if self.isActive() else 0
    
    def applyThrust(self, dt):
        return self.getThrust() * self._thrustLevel, 0

    def setThrustLevel(self, level):
        self._thrustLevel = min(1, max(0, level))

    def getFuelMass(self):
        return 0
    

class CruiseEngine(EngineBase):
    def __init__(self, thrust, fuelMass0, workingTime, height, mass=0):
        super().__init__(thrust, mass, height)

        self._fuelMass = fuelMass0
        self._dFuelMassDt = fuelMass0 / workingTime
        self._workingTime = workingTime

    def getFuelMassDt(self):
        return self._dFuelMassDt

    def getFuelMass(self):
        return self._fuelMass
    
    def getMass(self):
        return super().getMass() + self.getFuelMass()

    def active(self):
        if self.getFuelMass() > 0:
            super().active()

    def applyThrust(self, dt):
        self._fuelMass = max(0, self.getFuelMass() - self.getFuelMassDt() * dt)

        if self.getFuelMass() <= 0:
            self.inactive()

        return super().applyThrust(dt)


class ManeuveringThruster(EngineBase):
    # direction:
    # 1 - ccw
    # -1 - cw
    def __init__(self, thrust, height, direction):
        super().__init__(thrust)

        self._height = height
        self._direction = direction
        self._thrustLevel = 0

    def setThrustLevel(self, level):
        self._thrustLevel = min(1, max(0, level))

    def getMoment(self):
        return self._height * self._direction * self._thrustLevel * self.getThrust() 

    def applyThrust(self, dt):
        return 0, self.getMoment()