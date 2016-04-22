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

    def combineValuesAtPoint(self, pt, v1, v2):
        """ Combine two overlapping values """
        #TODO: can we extend to more than 2? 
        return v1+v2

    def spreadValueAtPoint(self, pt, oldNeighbors):
        """ return 9 values to be applied:
                [(x-1, y-1),  (x, y-1),  (x+1, y-1)
                 (x-1, y),     ( pt ),   (x+1, y)
                 (x-1, y+1),  (x, y+1),  (x+1, y+1)]  
            oldNeighbors is given in the same format """
        return oldNeighbors

    def update(self):
        startX = None
        startY = None
        endX = None
        endY = None

        for o in self.objectList:
            pt1 = o.influencingRegion()
            pt2 = o.influencedByRegion()

    def addObject(self, o):
        self.objectList.append(o)

