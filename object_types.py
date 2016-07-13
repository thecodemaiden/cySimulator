class PhysicalObject(object):
    """Common methods for objects that are part of the physical simulation"""
    def __init__(self, environment):
        self.environment = environment

    def update(self, dt):
        pass

    def drawExtras(self):
        pass

    def onVisualizationStart(self):
        pass

class FieldObject(object):
    def getRadiatedValue(self):
        pass
    def getPosition(self):
        pass

class FieldSphere(object):
    def __init__(self, center, totalPower):
        # TODO: waves have wavelengths
        self.totalPower = totalPower
        self.center = center
        self.radius = 0 # TODO: make this an epsilon?
        self.intensity = self.totalPower # LOL wut

class Field(object):
    # TODO: take material into account
    def __init__(self, propSpeed, minIntensity):
        # TODO: replace with sphereList, mapping sphere to producing object
        self.objects = {}
        self.speed = propSpeed
        self.minI = minIntensity

    def getAttenuationFactor(self, distance):
        return 1.0/(distance**2)

    def addObject(self, o):
        self.objects[o] = []

    def update(self,dt):
        for o,sphereList in self.objects.items():
            newSphere = FieldSphere(o.getPosition(), o.getRadiatedValue())
            newSphereList = [newSphere]
            for s in sphereList:
                # we need to expand it, and if power density is too low, remove it
                s.radius += dt*self.speed
                s.intensity = s.totalPower/(s.radius**2)
                if s.intensity >= self.minI:
                    newSphereList.append(s)
            self.objects[o] = newSphereList 






