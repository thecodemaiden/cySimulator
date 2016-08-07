import gc
import numpy as np

class FieldObject(object):
    def getPosition(self):
        pass
    def getRadiatedValue(self):
        return None
    def getMaxRadiatedValue(self):
        return None # DUNNO
    def detectField(self, fieldValue):
        """Register any readings, if necessary. fieldvalue is a FieldSphere
           Return True if this wave was handled, False otherwise (and it may show up again) """
        return False

class FieldSphere(object):
    def __init__(self, center, totalPower, data=None):
        # TODO: waves have wavelengths
        self.totalPower = totalPower
        self.center = center
        self.radius = 0 # TODO: make this an epsilon?
        self.lastRadius = 0
        self.intensity = None# LOL wut
        self.data = data

class Field(object):
    def __init__(self, propSpeed):
        # TODO: replace with sphereList, mapping sphere to producing object
        self.objects = {}
        self.speed = propSpeed

    def addObject(self, o):
        self.objects[o] = []

    def removeObject(self, o):
        self.objects.pop(o, None)

    def _sphereGenerator(self):
        for sphereList in self.objects.itervalues():
            for s in sphereList:
                yield s

    def performIntersections(self):
        '''We need to go through all spheres and find intersections between objects and spheres with radius>0'''
        # assumes waaay more spheres than objects
        # TODO: octree or other representation to limit comparisons
        allSpheresList = self._sphereGenerator()
        for s in allSpheresList:
            if s.radius == 0: continue
            for o in self.objects:
                # TODO: maintain object positions????
                dCenters = np.linalg.norm(np.array(s.center)-np.array(o.getPosition()))
                # TODO: obstacles
                if dCenters == s.radius:
                    o.detectField(s)
                elif dCenters > s.lastRadius and dCenters< s.radius:
                    # TODO: we need to roll back to time of intersection
                    copySphere = FieldSphere(s.center, s.totalPower, s.data)
                    copySphere.intensity = s.totalPower/dCenters
                    o.detectField(copySphere)

    def updateSphereValue(self, s, dt):
         # we need to expand it, and if power density is too low, remove it
        if s.intensity is not None and s.intensity < self.minI:
            return None
        s.lastRadius = s.radius
        s.radius += dt*self.speed
        s.intensity = s.totalPower/(s.radius**2)
        return s

    def spawnSphereFromObject(self, o):
        newSphere = FieldSphere(o.getPosition(), o.getRadiatedValue())
        return newSphere

    def update(self,dt):
        # TODO: modify in-place
        gc.disable()
        for o,sphereList in self.objects.items():
            newSphereList = []
            newSphere = self.spawnSphereFromObject(o)
            if newSphere is not None:
                newSphereList.append(newSphere)
            for s in sphereList:
               newS = self.updateSphereValue(s, dt)
               if newS is not None:
                   newSphereList.append(newS)
            self.objects[o] = newSphereList
        gc.enable()
        self.performIntersections()


class VectorField(Field):
    # TODO: real vector shit
    def __init__(self, propSpeed, minIntensity):
        super(VectorField, self).__init__(propSpeed)
        self.minI = minIntensity

class SemanticField(Field):
    def __init__(self, propSpeed, minIntensity):
        super(SemanticField, self).__init__(propSpeed)
        self.minI = minIntensity

    def spawnSphereFromObject(self, o):
        val = o.getRadiatedValue()
        if val is not None:
            newSphere = FieldSphere(o.getPosition(), val[0], val[1])
            return newSphere
        return None






