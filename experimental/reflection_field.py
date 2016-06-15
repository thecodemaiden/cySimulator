from collections import namedtuple

class ReflectionPlane(object):
    def __init__(self, origin, extent):
        self.origin = tuple(origin)
        self.extent = list(extent)
        # make sure it is not a line or a box
        assert((0 in self.extent) and (self.extent.count(0) == 1))
        # whichever part of the extent is 0 is the normal axis
        self.normal_axis = self.extent.index(0)






class ReflectionInfo(object):
    def __init__(self, original):
        self.parent = parent
        self.children = []
        self.plane = plane

    def updateChildren(self,