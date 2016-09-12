import gc
import numpy as np
import threading
import Queue as queue
from multiprocessing.pool import ThreadPool
from collections import defaultdict
import itertools as it

def fixPhase(a):
    return ( a + np.pi) % (2 * np.pi ) - np.pi

class FieldObject(object):
    def getPosition(self):
        pass
    def getRadiatedValues(self):
        return [(None, None)]
    def getMaxRadiatedValue(self):
        return None # DUNNO
    def detectField(self, fieldValue):
        """Register any readings, if necessary. fieldvalue is a FieldSphere
           Return True if this wave was handled, False otherwise (and it may show up again) """
        return False
    def getPendingEmission(self):
        # return (intensity, startTime, endTime)
        pass

class FieldSphere(object):
    startR = 0.00001
    def __init__(self, center, speed, frequency, totalPower, startTime, data=None):
        # TODO: waves have wavelengths
        self.totalPower = totalPower
        self.center = tuple(center)
        self.radius = self.startR # TODO: make this an epsilon?
        self.lastRadius = 0
        self.intensity = None# LOL wut
        self.data = data
        self.t1 = startTime
        self.center_2 = sum([k*k for k in self.center])
        self.obj_distances = {}
        self.speed = speed
        self.isPlanar = False
        self.frequency = frequency
        self.onSurface = [0,0,0,0] # [a, b, c, d] for ax+by+cz = d
        self.reflect_limits = [None, None] # xy angle, zy angle

    def reflectOffSurface(self, surfPos, surfSize):
        # first get the vector from our source to the surface
        # so we can reflect ourselves on the other side of that
        dPos = [a-b for a,b in zip(surfPos, self.center)] #surf-self

        reflectPos = [a+b for a,b in zip(dPos, surfPos)]

        newLimits = [a+b for a,b in zip(surfPos, surfSize)]+[a-b for a,b in zip(surfPos, surfSize)]

        # really naive: waves don't exist above/below the surface (plane reflection...)
        # determine the 'side' of the surface we are on, and don't spread back around the object
        # ignore edges...
        if dPos[0] > 0:
            # surf_x > self_x, so 
            self.reflect_limits[0] = -np.inf
        if dPos[0] < 0:
            self.reflect_limits[3] = np.inf
            self.r
        if dPos[1] > 0:
            # surf_x > self_x, so 
            self.reflect_limits[1] =- np.inf
        if dPos[1] < 0:
            self.reflect_limits[4] = -np.inf
        if dPos[2] > 0:
            # surf_x > self_x, so 
            self.reflect_limits[2] = -np.inf
        if dPos[2] < 0:
            self.reflect_limits[2] = -np.inf

        reflected = FieldSphere(reflectPos, self.speed, self.frequency, self.totalPower, self.t1, self.data)
        reflected.reflect_limits = self.reflect_limits

        return reflected

    def prepareToDiscard(self, t):
        self.lastRadius = self.radius
        self.radius = self.speed*(t-self.t1)
       
        if self.radius > 0:
            self.intensity = self.totalPower/(self.radius*self.radius)

    def calculate(self, obj, obj_pos, obj_pos_sq):
        x1, y1, z1 = self.center
        x,y,z = obj_pos

        order2 = 2*x*x1 + 2*y*y1 + 2*z*z1
       
        newDist = obj_pos_sq + self.center_2 - order2
        oldDist = self.obj_distances.get(obj, newDist)

        self.obj_distances[obj] = newDist

        if (self.radius*self.radius >= newDist) and (self.lastRadius*self.lastRadius < oldDist):
            return True
        return False

    @classmethod
    def copyAtT(cls, oldS, t, speed):
        newS =  cls(oldS.center, oldS.speed, oldS.frequency, oldS.totalPower, oldS.t1)
        newS.radius = speed*(t-oldS.t1)
        newS.data = oldS.data
        if newS.radius > 0:
            newS.intensity = newS.totalPower/(newS.radius*newS.radius)

        return newS


class Field(object):
    sharedThreadPool = ThreadPool(4) 
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

    def _intersectionThreaded(self, args):
        s = args[0]
        info = args[1]
        intersectInfo = {}
        if s.intensity is not None:
            for o in self.objects:
                objInfo = info[o]
                if s.calculate(o, objInfo[0], objInfo[1]):
                    dPos = np.subtract(objInfo[0], s.center)
                    dt = np.linalg.norm(dPos)/self.speed
                    properCopy = FieldSphere.copyAtT(s, s.t1+dt, self.speed)
                    intersectInfo[o] = properCopy
        return intersectInfo
                

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

        repeatInfo = it.repeat(objInfoTable)
        allSpheresList = self._sphereGenerator()
        together = it.izip(allSpheresList, repeatInfo)
        allIntersections = self.sharedThreadPool.imap_unordered(self._intersectionThreaded, together, 8)
        # now take the collisions and order them by object
        intersectionsByObject = defaultdict(list)
        for intersect in allIntersections:
            for o in intersect:
                intersectionsByObject[o].append(intersect[o])
        for o,sList in intersectionsByObject.items():
            # TODO: combine wavefronts that interfere
            newWave = self.combineValues(sList)
            o.detectField(newWave)
           

    def _obstacleThreaded(self, args):
        s = args[0]
        obs = args[1]
        bouncy = None
        # if the distance from us to the obstacle <= our radius, it intersects
        depth = obs.geom.pointDepth(s.center)
        if depth < 0 and -depth <= s.radius:
             bouncy = s.reflectOffSurface(obs.centerPos, obs.dim)
        return bouncy
        

    def intersectObstacles(self, obsList):
        allSpheresList = self._sphereGenerator()
        for obs in obsList:
            rep = it.repeat(obs)
            newSpheres = self.sharedThreadPool.map(self._obstacleThreaded, it.izip(allSpheresList, rep))              

             
    def update(self, now):
        # TODO: modify in-place
        allObjects = self.objects.iterkeys()
        for o in allObjects:
            sphereList = self.objects[o]
            newSpheres = self.spawnSphereFromObject(o, now) # TODO: check frequency!
            for newSphere in newSpheres:
                newSphere.obj_distances[o] = 0
                sphereList.append(newSphere)
            for s in sphereList:
                s.prepareToDiscard(now)
        self.performIntersections(now)
        for o in allObjects:
            toRemove = []
            for s in self.objects[o]:
                if s.intensity is not None and s.intensity < self.minI:
                        toRemove.append(s)
            newList = [s for s in sphereList if s not in toRemove]
            self.objects[o] = newList

    def spawnSphereFromObject(self, o, t):
        sphereList = []
        allNew = o.getRadiatedValues()
        for info in allNew:
            if info is None or info[0] <= 0 or info[1] <= 0:
                continue
            freq, power = info
            newSphere = FieldSphere(o.getPosition(), self.speed, freq, power, t)
            sphereList.append(newSphere)
        return sphereList

    def combineValues(self, sphereList):
        return sphereList[0]

class VectorField(Field):
    # TODO: real vector shit
    def __init__(self, propSpeed, minIntensity):
        super(VectorField, self).__init__(propSpeed)
        self.minI = float(minIntensity)

class SemanticField(Field):
    def __init__(self, propSpeed, minIntensity):
        super(SemanticField, self).__init__(propSpeed)
        self.minI = float(minIntensity)

    def combineValues(self, sphereList):
        if len(sphereList) == 1:
            return sphereList[0]

        intensities, phases = zip(*[(s.intensity, (2*np.pi*s.radius*s.frequency)) for s in sphereList])
        polard = np.dot(intensities, np.exp(1j*np.array(phases)))
        strongest = intensities.index(max(intensities))
        polar_sum = np.sum(polard)
        newIntensity = np.abs(polar_sum)

        newSphere = FieldSphere((0,0,0), 0, 0, 0, 0, sphereList[strongest].data)
        newSphere.intensity = newIntensity

        return newSphere

    def spawnSphereFromObject(self, o,t):
        sphereList = []
        allNew = o.getRadiatedValues()
        for info in allNew:
            if info is None or info[0] is None:
                continue
            freq, val = info[0]
            data = info[1]
            newSphere = FieldSphere(o.getPosition(), self.speed, freq, power, t, data)
            sphereList.append(newSphere)
        return sphereList






