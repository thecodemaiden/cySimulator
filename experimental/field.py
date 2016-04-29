#!/usr/bin/python2
import numpy as np

class FieldObject(object):
    """ An object that is influences or influences a field in its area """
    def __init__(self, **kwargs):
        #super(FieldObject, self).__init__()
        pass

    def influencingRegion(self):
        """ Returns two points that define a bounding box for the direct influence of the object"""
        #TODO: needs a much clearer name
        return [(0,0,0), (0,0,0)]

    def influencedByRegion(self):
        """ Returns two points to define a bounding box for field values needed to update the object"""
        return [(0,0,0), (0,0,0)]
    
    def transformFieldValueAtPoint(oldVal, pt):
        """ Modify the field value at the point (add, subtract) if needed """
        return oldVal

    def getRadiatedValue(self):
        return 0

class FieldInfluence(object):
    def __init__(self, center, radius, magnitude):
        self.center = tuple(center)
        self.r = radius
        self.mag = magnitude

class SphereField(object):
    """ TODO: document me! """
    def __init__(self, name, spreadVector, stopValue=1e-1):
        ''' spread is [vel, mag_factor] '''
        super(SphereField, self).__init__()
        self.name = name
        self.objectList = set()
        self.stopValue = stopValue
        self.spread = spreadVector
        self.sphereList = [] # store center, radius, mag
        self.initialRadius = 0 # wut

    def addObject(self, o):
        self.objectList.add(o)

    def update(self, dt):
        # spread exisiting spheres
        newList = []
        for s in self.sphereList:
            newMag = s.mag * np.exp(-dt/self.spread[1])
            if newMag > self.stopValue:
                newR = s.r + self.spread[0]*dt
                newList.append(FieldInfluence(s.center, newR, newMag))
        self.sphereList = newList

        # add new ones
        for o in self.objectList:
            v = o.getRadiatedValue()
            p = o.pos
            self.sphereList.append(FieldInfluence(p, self.initialRadius, v))

class Field(object):
    """ TODO: document """
    def __init__(self, name, defaultValue=0.0, granularity=5.0):
        super(Field, self).__init__()
        self.name = name
        self.objectList = [] # all the objects that affect and are affected by the field
        self.steadyStateValue = defaultValue
        self.gran = granularity

    def addObject(self, o):
        self.objectList.append(o)

    def getValueAtPoint(self, pt):
        """ Return current value of field (can be vector, scalar, other) """
        return 0.0    

    def combineValuesAtPoint(self, pt, values):
        """ Combine two overlapping values """
        return sum(values)

    def update(self,dt):
        pass

    def addObject(self, o):
        self.objectList.append(o)

