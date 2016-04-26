#!/usr/bin/python2

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

