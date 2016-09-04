import gc
import numpy as np
import threading
import Queue as queue
from multiprocessing.pool import ThreadPool
from collections import defaultdict
import itertools as it

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
        self.lastRadius = 0
        self.intensity = None# LOL wut
        self.data = data
        self.t1 = startTime
        self.center_2 = sum([k*k for k in self.center])
        self.obj_distances = {}

    def prepareToDiscard(self, t, speed):
        self.lastRadius = self.radius
        self.radius = speed*(t-self.t1)
       
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
        newS =  cls(oldS.center, oldS.totalPower, oldS.t1)
        newS.radius = speed*t
        return newS


class Field(object):
    sharedThreadPool = ThreadPool(8) 
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
                    toa = (objInfo[0][0] - s.center[0])/self.speed + s.t1
                    intersectInfo[o] = s
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
            o.detectField(sList[0])
            

            

    def update(self, now):
        # TODO: modify in-place
        allObjects = self.objects.iterkeys()
        for o in allObjects:
            toRemove = []
            sphereList = self.objects[o]
            newSphere = self.spawnSphereFromObject(o, now) # TODO: check frequency!
            if newSphere is not None:
                newSphere.obj_distances[o] = 0
                sphereList.append(newSphere)
            for s in sphereList:
                s.prepareToDiscard(now, self.speed)
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

    '''
class FieldManagementThread(threading.Thread):
    def __init__(self):
        super(FieldManagementThread, self).__init__()
        self.daemon = True
        self.fields = {}
        self.fieldAddQueue = queue.Queue()
        self.fieldRemoveQueue = queue.Queue()

        # a dictionary, per field
        # within it,
        self.intersectionInfo = {}

    def addField(self, f, name):
        self.fieldAddQueue.put((f,name))

    def removeField(self, name):
        self.fieldRemoveQueue.put(name)

    def run(self):
        # Add and remove from queue
        try:
            while(True):
                field, name = self.fieldAddQueue.get(False)
                if name not in self.fields:
                    self.fields[name] = field
        except queue.Empty:
            pass

        try:
            while(True):
                name = self.fieldRemoveQueue.get(False)
                self.fields.pop(name, None)
        except queue.Empty:
            pass

        # now do the field stuff

        '''








