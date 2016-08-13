import ode
import logging

from field_types import Field
from heatmap import Heatmap
import numpy as np

from time import time


class FieldDrawingManager():
    import visual as v
    def __init__(self):
        self.sphereDisplay = {}
        self.maxI = -50
        self.minI = -50
        self.lThreshold = 1.0

    def addWavefront(self, sphere):
        if sphere not in self.sphereDisplay:
            actor = self.v.sphere()
            actor.pos = sphere.center
            actor.radius = sphere.radius
            self.sphereDisplay[sphere] = actor


    def removeWavefront(self, sphere):
        s = self.sphereDisplay.pop(sphere, None)
        if s is not None:
            s.visible= False
            #del s

    def reset(self):
        for s in self.sphereDisplay.values():
            s.visible = False
        self.sphereDisplay.clear()
    
    def refreshIntensityLimits(self):
        # search through spheres to find max, min
        spheres = self.sphereDisplay.keys()
        self.maxI = max(spheres, key=lambda x:x.intensity).intensity
        self.minI = min(spheres, key=lambda x:x.intensity).intensity


    def updateView(self, currentSpheres):
        actors = self.sphereDisplay
        toRemove = [s for s in actors if s not in currentSpheres or s.radius > self.lThreshold]
        toAdd = [s for s in currentSpheres if s not in actors and s.radius <= self.lThreshold]

        for s in toRemove:
            self.removeWavefront(s)

        for s in toAdd:
            self.addWavefront(s)

        # update next tick...
        for s, g in self.sphereDisplay.items():
            i = np.log(s.intensity)
            
            intensityColor = Heatmap.getHeatmapValue(i, self.minI, self.maxI)
            g.color = intensityColor
            g.opacity = 0.3
            g.radius = s.radius

class PhysicalEnvironment():
    def __init__(self, manager):
        self.world = ode.World()
        self.space = ode.HashSpace()
        self.lengthScale = 1.0#10.0
        self.massScale = 1.0# 10.0 # now a unit is 10g, not 1kg...
        self.forceScale = self.massScale*self.lengthScale
        self.manager = manager
        self.fieldList = {}
        self.drawField = False

        self.world.setGravity((0,-9.81*self.forceScale,0))
        self.world.setCFM(1e-5)
        self.world.setERP(0.8) # seems to make the collision behavior more stable
        self.world.setContactSurfaceLayer(0.001)

        self.contactGroup = ode.JointGroup()

        self.objectList = []

    def start(self):
        for o in self.objectList:
            o.onVisualizationStart()

    def addField(self, fieldName, f):
        self.fieldList[fieldName] = {'field':f, 'display':{}}

    def addFieldObject(self, fieldName, o):
        # TODO: error behavior
        fieldInfo = self.fieldList[fieldName]
        fieldInfo['field'].addObject(o)
        d = FieldDrawingManager() # TODO: option to specify which spheres must be drawn
        fieldInfo['display'][o] = d

    def addObject(self, obj):
        # assumes body is already in our world, and collision geoms are in our space
        self.objectList.append(obj)

    def update(self, dt):
        for o in self.objectList:
            o.updatePhysics(dt)
        # then update the field
        for f in self.fieldList.values():
            field = f['field']
            field.update(dt)
            if self.drawField:
                managers = f['display']
                for obj, wfs in field.objects.items():
                    display = managers[obj]
                    display.updateView(wfs)

        self.space.collide(None, self.near_callback)
        self.world.quickStep(dt)
        self.contactGroup.empty()

    def near_callback(self, args, geom1, geom2):
        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # Create contact joints
        for c in contacts:
            c.setBounce(0.7)
            c.setMu(500)
            j = ode.ContactJoint(self.world, self.contactGroup, c)
            j.attach(geom1.getBody(), geom2.getBody())

class ComputeEnvironment():
    def __init__(self, manager):
        self.taskList = []
        self.manager = manager

    def start(self):
        pass

    def update(self, dt):
        pass

class SimulationManager():
    """ Contains the physical + computational simulation loops, and any visualization"""
    def __init__(self, dt):
        self.physicalEnvironment = PhysicalEnvironment(self)
        self.computeEnvironment = ComputeEnvironment(self)
        self.draw = True
        self.visualizer = None
        self.dt = dt;

    def setVisualizer(self, vClass, *args):
        if self.visualizer is not None:
            self.visualizer.cleanup()
        self.visualizer = vClass(self.physicalEnvironment, *args)

    def start(self):
        self.visualizer.create()
        self.physicalEnvironment.start()

    def runloop(self):
        from visual import rate
        try:
            while True:
                self.physicalEnvironment.update(self.dt)
                self.computeEnvironment.update(self.dt)
                if self.visualizer is not None:
                    self.visualizer.update(self.dt)
                    rate(1.0/self.dt)
        except KeyboardInterrupt:
            print("Interrupted")

