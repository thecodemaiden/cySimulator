#!/usr/bin/python2
from random import uniform
from common import Point3d
import logging

#TODO: print logs

class MobileObject(object):
    def __init__(self, **kwargs):
        world = kwargs['world'] # necessary
        name = kwargs.get('name', 'MobileObject')

        #super(MobileObject, self).__init__()
        self.pos = Point3d(0,0,0)
        self.v = (0,0,0)
        self.dest = Point3d(0,0,0)
        self.world = world
        self.name = name

        self.world.addEntity(self)

    def position_update(self):
        togoX = self.dest.x - self.pos.x
        togoY = self.dest.y - self.pos.y
        togoZ = self.dest.z - self.pos.z


        if (abs(togoX) <= abs(self.v[0])):
            newX = self.dest.x
            self.v = (0, self.v[1], self.v[2])
        else:
            newX = self.pos.x + self.v[0]

        if (abs(togoY) <= abs(self.v[1])):
            newY = self.dest.y
            self.v = (self.v[0], 0, self.v[2])
        else:
            newY = self.pos.y + self.v[1]

        if (abs(togoZ) <= abs(self.v[2])):
            newZ = self.dest.z
            self.v = (self.v[0], self.v[1], 0)
        else:
            newZ = self.pos.z + self.v[2]

        self.pos = Point3d(newX, newY, newZ)
           
        #print("[{}]\tpos: {:5.2f},{:5.2f},{:5.2f}\tdest: {:5.2f},{:5.2f},{:5.2f}".format(self.name, *(self.pos + self.dest)))

        if self.v == (0,0,0):
            self.changeDest()


    def changeDest(self):
        destX = uniform(-self.world.xLength/2,self.world.xLength/2)
        destY = uniform(-self.world.yLength/2,self.world.yLength/2)
        destZ = uniform(-self.world.zLength/2,self.world.zLength/2)

        moveV = uniform(20, 100)
        Vx = (destX -self.pos.x)/moveV
        Vy = (destY -self.pos.y)/moveV
        Vz = (destZ -self.pos.z)/moveV


        self.dest = Point3d(destX, destY, destZ)
        self.v = (Vx, Vy, Vz)
