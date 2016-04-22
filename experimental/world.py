#!/usr/bin/python
#from field import Field

class World(object):
    def __init__(self, xLength, yLength, zLength):
        super(World, self).__init__()
        self.xLength = float(xLength)
        self.yLength = float(yLength)
        self.zLength = float(zLength)
        self.entityList = set()
        self.fieldList = set()

    def addEntity(self, o):
        self.entityList.add(o)

    def addField(self,f):
        # TODO: names must be unique
        self.fieldList.add(f)

    def registerToField(self, o, fieldName):
        for e in self.fieldList:
            if e.name == fieldName:
                e.addObject(o)
        self.entityList.add(o) # does nothing if already added

    def update(self):
        for f in self.fieldList:
            f.update()
        for o in self.entityList:
            o.update()
