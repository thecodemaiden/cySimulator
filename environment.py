import ode
import logging
import vtk
from vtk import vtkCamera
from object_types import Field
from heatmap import Heatmap
import numpy as np
from odeViz.ode_visualization import ODE_Visualization

from time import time
#TODO: scale the world...
# scaling lengths (m->cm)
#

class MyVisualization(ODE_Visualization):
    def __init__(self, world, space, env, dt):
        super(MyVisualization, self).__init__(world, space, dt)
        self.camera = vtkCamera()
        self.camera.SetFocalPoint((0,0,0))
        self.camera.SetPosition((0, 0, 13*env.lengthScale))
        self.ren.SetActiveCamera(self.camera)

        self.contactGroup = ode.JointGroup()
        self.environment = env
        self.logger = self.environment.logger
        
        self.frametime = 1.0/30000000 #1/fps
        self.frameAccum = 0 # when this hits >= frametime, set to 0 and repaint

    def execute(self, caller, event):
        n = 10
        for i in range(n):
            self.environment.update(self.dt/n)
            self.space.collide(None, self.near_callback)
            self.step(self.dt/n)
            self.contactGroup.empty()
        self.environment.drawExtras()
        if self.frameAccum >= self.frametime:
            self.update() # do not forget ...
            self.environment.nFrames += 1
            self.frameAccum = 0
        else:
            self.updateStatus()
        self.frameAccum += self.dt
        if self.environment.nFrames % 100 == 1:
               self.logger.info("Effective frame rate: {}".format(self.environment.getMeanFramerate()))


    def near_callback(self, args, geom1, geom2):
        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # Create contact joints
        for c in contacts:
            c.setBounce(0.7)
            c.setMu(500)
            j = ode.ContactJoint(self.world, self.contactGroup, c)
            j.attach(geom1.getBody(), geom2.getBody())


class Environment(object):
    def __init__(self, dt=0.1, windowW=1024, windowH=768):
        super(Environment, self).__init__()
        self.logger = logging.getLogger(name='Quadsim.Environment')
        self.logger.setLevel(logging.DEBUG)

        self.world = ode.World()
        self.space = ode.Space()
        self.lengthScale = 1.0#10.0
        self.massScale = 1.0# 10.0 # now a unit is 10g, not 1kg...
        self.forceScale = self.massScale*self.lengthScale

        self.dt = dt/self.lengthScale;

        self.fieldList = {}

        self.world.setGravity((0,-9.81*self.forceScale,0))
        self.world.setCFM(1e-5)
        self.world.setERP(0.8) # seems to make the collision behavior more stable
        self.world.setContactSurfaceLayer(0.001)

        self.objectList = []

        groundY = -10
        
    def addField(self, fieldName, f):
        self.fieldList[fieldName] = {'field':f, 'display':{}}

    def addFieldObject(self, fieldName, o):
        # TODO: error behavior
        fieldInfo = self.fieldList[fieldName]
        fieldInfo['field'].addObject(o)

    def createFieldSphere(self, sphereData):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*sphereData.center)
        sphere.SetRadius(sphereData.radius)
        sphere.SetPhiResolution(15)
        sphere.SetThetaResolution(15)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(0.1)

        actor.backingSphere = sphere

        return actor

    def drawExtras(self):
        for o in self.objectList:
            o.drawExtras()
        # draw field stuff
        THRESHOLD = 1.0*self.lengthScale
        for fInfo in self.fieldList.values():
            field = fInfo['field']
            obj = field.objects.keys()[0]
            spheres = field.objects[obj]
            actors = fInfo['display']

            maxIntensity = np.log(obj.getRadiatedValue()) #TODO: this may change, find another max
            minIntensity = np.log(field.minI)
            toRemove = [s for s in actors if s not in spheres or s.radius > THRESHOLD]
            toAdd = [s for s in spheres if s not in actors and s.radius <= THRESHOLD]
            # first remove all the ones that need removing
            for s in toRemove:
                a = actors.pop(s, None)
                if a is not None:
                    self.sim.ren.RemoveActor(a)
            # then update the ones that need updating 
            for sphere,actor in actors.items():
                bs = actor.backingSphere
                bs.SetRadius(sphere.radius)
                intensityColor = Heatmap.getHeatmapValue(np.log(sphere.intensity), minIntensity, maxIntensity)
                actor.GetProperty().SetColor(*intensityColor)
                #actor.Update()
            for sphere in toAdd:
                actor = self.createFieldSphere(sphere)
                intensityColor = Heatmap.getHeatmapValue(np.log(sphere.intensity), minIntensity, maxIntensity)
                actor.GetProperty().SetColor(*intensityColor)
                actors[sphere] = actor
                self.sim.ren.AddActor(actor)
           

    def getGeomVizProperty(self, g):
        return self.sim.GetProperty(g)


    def addObject(self, obj):
        # assumes body is already in our world, and collision geoms are in our space
        self.objectList.append(obj)

    def start(self):
        self.sim = MyVisualization(self.world, self.space, self, self.dt)
        for o in self.objectList:
            o.onVisualizationStart()
        self.startTime = time()
        self.nFrames = 0
        self.sim.start()

    def getMeanFramerate(self):
        now = time()
        return float(self.nFrames)/(now - self.startTime)

    def update(self, dt):
        for o in self.objectList:
            o.update(dt)
        # then update the field
        for f in self.fieldList.values():
            field = f['field']
            field.update(dt)



