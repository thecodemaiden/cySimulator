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
    startR = 0.00001
    def __init__(self, center, totalPower, startTime, data=None):
        # TODO: waves have wavelengths
        self.totalPower = totalPower
        self.center = center
        self.radius = self.startR # TODO: make this an epsilon?
        self.intensity = None# LOL wut
        self.data = data
        self.t1 = startTime
        self.t1_2 = self.t1*self.t1
        self.lastCheckTime = None
        self.lastTTerm = None
        self.center_2 = sum([k*k for k in self.center])
        self.obj_distances = {}

    def prepareToDiscard(self, t, ct_calc, speed):
        if self.lastCheckTime != t:
            self.lastCheckTime = t
            self.lastTTerm = ct_calc + (- 2*self.t1*t + self.t1_2)*speed
        # this is actually our current radius! see if we are too diminished
        self.radius = self.lastTTerm
        #if self.radius == 0:
        #    self.radius = self.startR
        if self.radius > 0:
            self.intensity = self.totalPower/self.radius# this is amplitude! (self.radius*self.radius)

    def calculate(self, obj, obj_pos, obj_pos_sq):
        # TODO: we can do bounding boxen
        x1, y1, z1 = self.center
        x,y,z = obj_pos
        # obj_pos_sq == x^2+y^2+z^2
        # ct_calc = ct^2
        order2 = 2*x*x1 + 2*y*y1 + 2*z*z1
       
        lhs = obj_pos_sq - order2 + self.center_2
        oldDist = self.obj_distances.get(obj, -1)
        newDist = lhs - self.lastTTerm
        self.obj_distances[obj] = newDist
        if newDist == 0 or (oldDist > 0 and newDist < 0):
            return True
        return False


class Field(object):
    def __init__(self, propSpeed, minI=1e-10):
        # TODO: replace with sphereList, mapping sphere to producing object
        self.objects = {}
        self.speed = float(propSpeed)
        self.minI = minI

    def addObject(self, o):
        self.objects[o] = []

    def removeObject(self, o):
        self.objects.pop(o, None)

    def _sphereGenerator(self):
        for sphereList in self.objects.itervalues():
            for s in sphereList:
                yield s

    def performIntersections(self, t):
        '''We need to go through all spheres and find intersections between objects and spheres with radius>0'''
        # assumes waaay more spheres than objects
        # TODO: octree or other representation to limit comparisons

        # precalculate obj. info
        objInfoTable = {}
        for o in self.objects:
            pos = o.getPosition()
            pos2 = sum([k*k for k in pos])
            objInfoTable[o] = (pos, pos2)

        allSpheresList = self._sphereGenerator()
        for s in allSpheresList:
            if s.intensity is None:
                continue
            for o in self.objects:
                info = objInfoTable[o]
                didIntersect = s.calculate(o, info[0], info[1])
                if didIntersect:
                    o.detectField(s)
                # TODO: is time rollback even necessary???

    def update(self, now):
        # TODO: modify in-place
        ctCalc = self.speed*now*now

        allObjects = self.objects.iterkeys()
        for o in allObjects:
            toRemove = []
            sphereList = self.objects[o]
            newSphere = self.spawnSphereFromObject(o, now) # TODO: check frequency!
            if newSphere is not None:
                newSphere.obj_distances[o] = 0
                sphereList.append(newSphere)
            for s in sphereList:
                s.prepareToDiscard(now, ctCalc, self.speed)
                if s.intensity is not None and s.intensity < self.minI:
                    toRemove.append(s)
            newList = [s for s in sphereList if s not in toRemove]
            self.objects[o] = newList
        self.performIntersections(now)

    def spawnSphereFromObject(self, o, t):
        newSphere = FieldSphere(o.getPosition(), o.getRadiatedValue(), t)
        return newSphere

class VectorField(Field):
    # TODO: real vector shit
    def __init__(self, propSpeed, minIntensity):
        super(VectorField, self).__init__(propSpeed)
        self.minI = float(minIntensity)

class SemanticField(Field):
    def __init__(self, propSpeed, minIntensity):
        super(SemanticField, self).__init__(propSpeed)
        self.minI = float(minIntensity)

    def spawnSphereFromObject(self, o,t):
        val = o.getRadiatedValue()
        if val is not None:
            newSphere = FieldSphere(o.getPosition(), val[0], t, val[1])
            return newSphere
        return None






