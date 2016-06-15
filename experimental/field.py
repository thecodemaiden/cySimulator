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
    def __init__(self, center, radius, magnitude, reflections=[]):
        self.center = tuple(center)
        self.r = radius
        self.mag = magnitude
        self.reflectFrom = list(reflections) # planes that have reflected it

class PlaneReflection(object):
    """ For use in the 'reflectFrom' field of FieldInfluence. 
        For simplicity, a plane 'x=5' should have origin (5,0,0) and normal (+-1, 0 , 0) 
    """
    def __init__(self, origin, normal):
        # whether normal is negative or positive determines if this is the reflected 'cap' or the 'main' sphere
        self.origin = tuple(origin) 
        self.normal = tuple(normal) # make immutable copies to avoid tragedy
   
    @classmethod
    def reflectSphereFieldOffPlane(cls, sphereField, planeAxis, planePos):
        """ Plane axis can be 0 (x = planePos), 1 (y=planePos), 2 (z = planePos) """
        # we need to decide if normal is posiitive or negative
        
        # first check that the plane even intersects (tangents don't count)
        #TODO: WTF do we do if dCenterToPlane == 0??

        dCenterToPlane = planePos - sphereField.center[planeAxis] 
        if dCenterToPlane < 0:
            edgePos = sphereField.center[planeAxis] - sphereField.r
            normalDirection = +1
        else:
            edgePos = sphereField.center[planeAxis] + sphereField.r
            normalDirection = -1

        if edgePos == planePos:
            # tangent, nothing to be done
            return [sphereField]

        planeOrigin = [0,0,0]
        planeOrigin[planeAxis] = planePos
        planeNormal = [0,0,0]
        planeNormal[planeAxis] = normalDirection

        # if we are already reflected off the same plane with opposite normal, there is nothing to be done
        for pr in sphereField.reflectFrom:
            if pr.origin == tuple(planeOrigin) and pr.normal[planeAxis] != 0:
                return [sphereField]

        # if normal direction == +1, we need edgePos to be < planePos
        # if normal direction == -1, we need edgePis to be > planePos
        if normalDirection*edgePos < planePos*normalDirection:
            # time to rebound
            newSphere1 = sphereField
            plane1 = PlaneReflection(planeOrigin, planeNormal)
            newSphere1.reflectFrom.append(plane1)

            # where is the center of the reflected sphere?
            # the distance to the plane must be the same, but it's now on the other side
            newCenter = list(sphereField.center)
            newCenter[planeAxis] = planePos + dCenterToPlane
            #planeNormal[planeAxis] = -normalDirection
            newSphere2 = FieldInfluence(newCenter, sphereField.r, sphereField.mag)
            #plane2 = PlaneReflection(planeOrigin, planeNormal)
            newSphere2.reflectFrom.append(plane1)

            return [newSphere1, newSphere2]

        return [sphereField]



        

    def getBoundingLimits(self):
        pass

class SphereField(object):
    """ TODO: document
        TODO: separate time/spread constant and velocity/wavelength params
    """
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

    def reflectSphereIfNeeded(self, s):
        return [s]

    def stepFieldSphere(self, s, dt):
        newMag = s.mag * np.exp(-dt/self.spread[1])
        if newMag > self.stopValue:
           newR = s.r + self.spread[0]*dt
           return FieldInfluence(s.center, newR, newMag,s.reflectFrom)
        else:
           return None

    def update(self, dt):
        # spread exisiting spheres
        newList = []
        for s in self.sphereList:
            newS = self.stepFieldSphere(s, dt)
            if newS is not None:
                reflected = self.reflectSphereIfNeeded(newS)
                newList += reflected
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

