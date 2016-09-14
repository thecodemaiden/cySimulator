import ode
import logging

from field_types import Field
from heatmap import Heatmap
import numpy as np

from time import time

class FieldVisualiser(object):
    import visual as v
    def __init__(self):
        self.visualWindow = None
        self.spheres = []
        self.colorList = [(255,255,0), (0,0,255),  (0,255,255), (0,255,0),(255,0,255), (255,0,0), ]
        
    def drawFieldState(self, field):
        if self.visualWindow is None:
            self.visualWindow = self.v.display(title='Field visualization', width=1024, height=768)
            #self.visualWindow.autocenter=False
            #self.visualWindow.scale = (0.05,0.05,0.05)
        self.visualWindow.select()
        for s in self.spheres:
            s.visible = False
        self.spheres = []
        i = 0
        for sphereList in [field.objects.values()[2]]:
            color = self.colorList[i]
            i += 1
            if i == len(self.colorList):
                i = 0
            for s in sphereList:
                sphere = self.v.sphere(pos=s.center, radius=s.radius/1000, color=color, opacity=0.2)
                self.spheres.append(sphere)
        


class PhysicalEnvironment(object):
    def __init__(self):
        super(PhysicalEnvironment, self).__init__()
        self.world = ode.World()
        self.space = ode.HashSpace()
        self.lengthScale = 1.0 
        self.massScale = 1.0 
        self.forceScale = self.massScale*self.lengthScale
        self.fieldList = {}

        self.world.setGravity((0,-9.81*self.forceScale,0))
        self.world.setCFM(1e-5)
        self.world.setERP(0.8) # seems to make the collision behavior more stable
        self.world.setContactSurfaceLayer(0.001)
        self.time = 0
        self.contactGroup = ode.JointGroup()

        self.objectList = [] 
        self.obstacleList = []       

    def addField(self, fieldName, f):
        self.fieldList[fieldName] = f
        f.environment = self

    def addFieldObject(self, fieldName, o):
        # TODO: error behavior
        fieldInfo = self.fieldList[fieldName].addObject(o)

    def addObstacle(self, obs):
        self.obstacleList.append(obs)

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
        div = 1

        for f in self.fieldList.values(): # TODO: make the fields into encapsualted 'physics objects'
            for i in range(div):
                oldTime += dt/div
                f.update(oldTime)
 
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
        timeout = 30.0
        startTime = 0#time()
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
                        elif chr == 't':
                            print self.time
                #if time()-startTime >= timeout:
                if self.time-startTime >= timeout:
                    break
              
        except KeyboardInterrupt:
            pass
        finally:
            # TODO: put this in cleanup function
            if self.visualizer is not None:
                self.visualizer.canvas.window.delete_all()


