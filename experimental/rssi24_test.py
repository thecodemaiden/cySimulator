from world import World
from mobile_object import MobileObject
from field import Field, FieldObject
from common import Rect3d
from time import time
import numpy as np
import vtk
from random import choice
from scipy.ndimage.filters import convolve

class RF24Strength(Field):
        def __init__(self, world, granularity=5.0):
            super(RF24Strength, self).__init__('RF24Strength', 1e-10, granularity)
            self.world = world
            worldSize = np.array([world.xLength/granularity, world.yLength/granularity, world.zLength/granularity], dtype=int)
            self.values  = np.full(worldSize, self.steadyStateValue)
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
            self.maxValue = self.minValue = self.steadyStateValue
            self.setupDraw()
           
        def dissipateFieldValues(self, dt):
            # take the old field values and dissipate them to the neighboring regions
            # to take dt into account, think of dissipation strength as the time constant
            dissipationStrength = 20 # very low value for TESTING - at time t+this, it will be at 37% strength
            nNeighbors = 27 #
            kernel = np.full((3,3,3), 1.0)
            newField = convolve(self.values, kernel, mode='constant') # get the sum of neighbouring values
            newField = newField/nNeighbors * np.exp(-dt/dissipationStrength) 

            self.values = newField


        def updateFieldValues(self, dt):
            # first, create a new field by dissipating the old values
            #self.dissipateFieldValues(dt)
            # then, add in the values from the radiating objects
            # TODO: all coordinates of first point must be less than or equal to values in second point
            originOffset = np.array([self.world.xLength/2, self.world.yLength/2, self.world.zLength/2])
            originOffset += self.gran
            for o in self.objectList:
                region = np.array(o.influencingRegion())
                
                # find the cells we need to look at
                cellRegion = np.array((region+originOffset)/self.gran, dtype='int32')
               
                if 0:
                    # TODO: can we ask clients to provide a convolution matrix?
                    # TODO: a single cell will not get anything done!
                    for cx in range(cellRegion[0,0], cellRegion[1,0]):
                        for cy in range(cellRegion[0,1], cellRegion[1,1]):
                            for cz in range(cellRegion[0,2], cellRegion[1,2]):
                                v = o.transformFieldValueAtPoint(self.values[cx,cy,cz], (cx,cy,cz))
                                self.values[cx,cy,cz] += v
                else:
                    # XXX: A HACK
                    v = o.transformFieldValueAtPoint(0, (0,0,0))
                    self.values[cellRegion[0,0]:cellRegion[1,0], cellRegion[0,1]:cellRegion[1,1],cellRegion[0,2]:cellRegion[1,2]] += v


        def update(self, dt):
            super(RF24Strength, self).update(dt)
            self.updateFieldValues(dt)

            logValues = np.log(self.values)

            self.maxValue = np.max(logValues)
            self.minValue = np.min(logValues)

            # assign colors to points
            colors = vtk.vtkUnsignedCharArray()
            colors.SetNumberOfComponents(3)
            colors.SetName('Colors')
            for v in np.nditer(logValues):
                #choose a random color for testing
                c = self.getHeatMapColor(v)
                colors.InsertNextTuple3(*c)

            #self.pointData.GetPointData().AddArray(colors)
            self.pointData.GetPointData().SetScalars(colors)
            self.pointData.GetPointData().SetActiveScalars('Colors')
            self.pointData.Modified()

        def setupDraw(self):
            p = vtk.vtkPoints()
            v = vtk.vtkCellArray()

            s = self.values.shape
            for x in range(s[0]):
                px = x*self.gran - self.world.xLength/2
                for y in range(s[1]):
                    py = y*self.gran - self.world.yLength/2
                    for z in range(s[2]):
                        pz = z*self.gran - self.world.zLength/2
                        id = p.InsertNextPoint(px,py,pz)
                        v.InsertNextCell(1)
                        v.InsertCellPoint(id)

            polyData = vtk.vtkPolyData()
            polyData.SetPoints(p)
            polyData.SetVerts(v)

            self.pointData = polyData

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(polyData)
            mapper.SetScalarVisibility(1)

            self.actor = vtk.vtkActor()
            self.actor.SetMapper(mapper)
            props = self.actor.GetProperty()
            props.SetPointSize(self.gran*2)
            props.SetOpacity(0.1)

        def getHeatMapColor(self, v):
            if (self.maxValue == self.minValue):
                idx = 0.5
            else:
                idx = (v - self.minValue)/(self.maxValue-self.minValue)
            idx = int(idx*(len(self.heatMapValues)-1))
            if idx < 15:
                idx = 0
            return self.heatMapValues[idx]



class MobileRFObject(MobileObject, FieldObject):
    def __init__(self, **kwargs):
        super(MobileRFObject, self).__init__(**kwargs)
        sz = kwargs.get('size', [0,0,0])
        self.size = sz
        self.boundaryStart = (self.pos.x-self.size[0]/2, self.pos.y-self.size[1]/2, self.pos.z-self.size[2]/2)
        self.boundaryEnd = (self.pos.x+self.size[0]/2, self.pos.y+self.size[1]/2, self.pos.z+self.size[2]/2)
        self.setupDraw()
        self.emissionStrength = 200
        
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

    def influencingRegion(self):
        """ Returns two points that define a bounding box for the direct influence of the object"""
        #TODO: needs a much clearer name
        return [self.boundaryStart, self.boundaryEnd]

    def influencedByRegion(self):
        """ Returns two points to define a bounding box for field values needed to update the object"""
        # let's only care about field value at our center, a single point
        return [self.pos, self.pos]
    
    def transformFieldValueAtPoint(self, oldVal, pt):
        """ Modify the field value at the point (add, subtract) if needed """
        return self.emissionStrength

    def update(self, dt):
        self.position_update(dt)
        self.boundaryStart = (self.pos.x-self.size[0]/2, self.pos.y-self.size[1]/2, self.pos.z-self.size[2]/2)
        self.boundaryEnd = (self.pos.x+self.size[0]/2, self.pos.y+self.size[1]/2, self.pos.z+self.size[2]/2)
        self.actor.SetPosition(*self.pos)
        # use influence of field

class DrawingWorld(World):
    def __init__(self, xLength, yLength, zLength, dt=0.1):
        super(DrawingWorld, self).__init__(xLength, yLength, zLength)
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.SetSize(800,600)
        self.renderWindow.AddRenderer(self.renderer)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renderWindow)
        self.dt = dt

        self.startTime = time()

    def startDrawing(self):
        self.iren.Initialize()

        self.iren.AddObserver('TimerEvent', self.update)
        self.iren.CreateRepeatingTimer(100)

        self.iren.Start()

    def addActor(self, a):
        self.renderer.AddActor(a)

    def update(self, event, obj):
        super(DrawingWorld, self).update(self.dt)
        self.renderWindow.Render()
        #if time() > self.startTime + 10:
        #   self.iren.TerminateApp()


w = DrawingWorld(200,200, 100)
f = RF24Strength(w)
w.addActor(f.actor)
m1 = MobileRFObject(world=w, name="zippy1", size=[10,10,10])
m2 = MobileRFObject(world=w, name="zippy2", size=[10,10,10])

w.addActor(m1.actor)
w.addActor(m2.actor)

w.registerToField(m1, 'RF24Strength')
w.registerToField(m2, 'RF24Strength')
w.startDrawing()
