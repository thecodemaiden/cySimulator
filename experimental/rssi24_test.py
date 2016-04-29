from world import World, DrawingWorld
from mobile_object import MobileObject
from field import SphereField, FieldObject, FieldInfluence
from time import time
import numpy as np
import vtk

from random import random

class RF24Strength(SphereField):
        def __init__(self, world):
            super(RF24Strength, self).__init__('RF24Strength', [50, 0.5])
            self.world = world
            self.world.addField(self)
            self.heatMapValues = np.array( [[36,    0,    0],
                                [73,    0,    0],
                                [109,    0,    0],
                                [146,    0,    0],
                                [182,    0,    0],
                                [219,    0,    0],
                                [255,    0,    0],
                                [255,   36,    0],
                                [255,   73,    0],
                                [255,  109,    0],
                                [255,  146,    0],
                                [255,  182,    0],
                                [255,  219,    0],
                                [255,  255,    0],
                                [255,  255,   43],
                                [255,  255,   85],
                                [255,  255,  128],
                                [255,  255,  170],
                                [255,  255,  213],
                                [255,  255,  255]], dtype='u1')
            self.maxValue = self.minValue = self.stopValue
            self.sphereActors = []

        def createSphereActor(self, s):
            """ given the FieldInfluence sphere, generate a vtk actor """
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(*s.center)
            sphere.SetRadius(s.r)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetOpacity(0.33333)

            return actor
       
        def update(self, dt):
            # remove all spheres - later we will do better
            for a in self.sphereActors:
                self.world.removeActor(a)

            self.sphereActors = []

            super(RF24Strength, self).update(dt)

            gatheredValues = [s.mag for s in self.sphereList]
            gatheredValues = np.log(gatheredValues)

            self.maxValue = max(gatheredValues)
            self.minValue = min(gatheredValues)

            for i in range(len(gatheredValues)):
                a = self.createSphereActor(self.sphereList[i])
                color = self.getHeatMapColor(gatheredValues[i])
                a.GetProperty().SetColor(*color)
                self.sphereActors.append(a)
                self.world.addActor(a)

        def getHeatMapColor(self, v):
            if (self.maxValue == self.minValue):
                idx = 0.5
            else:
                idx = (v - self.minValue)/(self.maxValue-self.minValue)
            idx = int(idx*(len(self.heatMapValues)-1))
            return self.heatMapValues[idx]

class MobileRFObject(MobileObject, FieldObject):
    def __init__(self, **kwargs):
        super(MobileRFObject, self).__init__(**kwargs)
        sz = kwargs.get('size', [0,0,0])
        self.size = sz
     
        self.setupDraw()
        self.emissionStrength = 2
        
    def setupDraw(self):
        cube = vtk.vtkCubeSource()
        cube.SetCenter(*self.pos)
        cube.SetXLength(self.size[0])
        cube.SetYLength(self.size[1])
        cube.SetZLength(self.size[2])

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetColor((1.0,1.0,1.0))
        self.actor.GetProperty().SetRepresentationToWireframe()

    def getRadiatedValue(self):
        return self.emissionStrength

    def update(self, dt):
        self.position_update(dt)
   
        self.actor.SetPosition(*self.pos)
        # use influence of field

w = DrawingWorld(200,200, 100)
f = RF24Strength(w)

for i in range(32):
    m = MobileRFObject(world=w, name="obj"+str(i), size=[10,10,10])
    w.addActor(m.actor)
    w.registerToField(m, 'RF24Strength')

#m1 = MobileRFObject(world=w, name="zippy1", size=[10,10,10])
#m2 = MobileRFObject(world=w, name="zippy2", size=[10,10,10])

#w.addActor(m1.actor)
#w.addActor(m2.actor)

#w.registerToField(m1, 'RF24Strength')
#w.registerToField(m2, 'RF24Strength')
w.startDrawing()
