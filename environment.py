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
            if s.intensity is None:
                continue
            i = np.log(s.intensity)
            
            intensityColor = Heatmap.getHeatmapValue(i, self.minI, self.maxI)
            g.color =  (0.0,1.0,0.0)#intensityColor
            g.opacity = 0.2
            g.radius = s.radius

class PhysicalEnvironment(object):
    def __init__(self):
        super(PhysicalEnvironment, self).__init__()
        self.world = ode.World()
        self.space = ode.HashSpace()
        self.lengthScale = 1.0 
        self.massScale = 1.0 
        self.forceScale = self.massScale*self.lengthScale
        self.fieldList = {}
        self.drawField = False

        self.world.setGravity((0,-9.81*self.forceScale,0))
        self.world.setCFM(1e-5)
        self.world.setERP(0.8) # seems to make the collision behavior more stable
        self.world.setContactSurfaceLayer(0.001)
        self.time = 0
        self.contactGroup = ode.JointGroup()

        self.objectList = []        

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

    def updatePhysics(self, dt):
        for o in self.objectList:
            try:
                o.updatePhysics(dt)
            except AttributeError:
                pass # maybe some things are pure computation?
        # then update the field... slowly
        oldTime = self.time
        div = 10

        for f in self.fieldList.values(): # TODO: make the fields into encapsualted 'physics objects'
            for i in range(div):
                oldTime += dt/div
                field = f['field']
                field.update(oldTime)
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

class ComputeEnvironment(object):
    def __init__(self):
        super(ComputeEnvironment, self).__init__()
        self.objectList = []
        self.time = 0

    def updateComputation(self, dt):
        for o in self.objectList:
            try:
                o.updateComputation(dt)
            except AttributeError:
                pass # not everything has computation

    def addObject(self, obj):
        # assumes body is already in our world, and collision geoms are in our space
        self.objectList.append(obj)


class SimulationManager(PhysicalEnvironment, ComputeEnvironment):
    """ Contains the physical + computational simulation loops, and any visualization"""
    def __init__(self, dt):
        super(SimulationManager, self).__init__()
        self.draw = True
        self.visualizer = None
        self.dt = dt;

    def setVisualizer(self, vClass, *args):
        if self.visualizer is not None:
            self.visualizer.cleanup()
        self.visualizer = vClass(self, *args)

    def start(self):
        if self.visualizer is not None:
            self.visualizer.create()
            for o in self.objectList:
                o.onVisualizationStart()
        self.time = 0

    def update(self):
        self.updateComputation(self.dt)
        self.updatePhysics(self.dt)
        self.time += self.dt

    def runloop(self):
        timeout = 20.0
        startTime = time()
        if self.visualizer is not None:
            self.visualizer.startTime = time()
            #self.visualizer.canvas.mouse.getclick()
        else:
            import msvcrt
            print 'Hit ESC to end'
            # TODO:  put keyboard input on separate thread...
        try:
            while True:
                self.update()
                if self.visualizer is not None:
                    self.visualizer.update(self.dt)
                else:
                    if msvcrt.kbhit():
                        chr = msvcrt.getche()
                        if ord(chr) == 27:
                            break
                if time()-startTime >= timeout:
                    break
              
        except KeyboardInterrupt:
            pass
        finally:
            # TODO: put this in cleanup function
            self.visualizer.canvas.window.delete_all()


