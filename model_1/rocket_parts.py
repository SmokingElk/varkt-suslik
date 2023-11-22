def getMassCenter(parts):
    massDotHeight = 0
    massSum = 0

    for i in parts:
        massDotHeight += i.getMass() * i.getHeight()
        massSum += i.getMass()

    return massDotHeight / massSum


def getInertiaMoment(parts):
    massCenter = getMassCenter(parts)
    return sum([i.getMass() * abs(i.getHeight() - massCenter)**2 for i in parts])


class Part:
    def __init__(self, mass, height):
        self._mass = mass
        self._height = height

    def getMass(self):
        return self._mass
    
    def getHeight(self):
        return self._height