from world import World
from mobile_object import MobileObject
from field import Field, FieldObject
from common import Rect3d
from time import time
import numpy as np
import vtk
from random import choice

class RF24Strength(Field):
        def __init__(self, world, granularity=10.0):
            super(RF24Strength, self).__init__('RF24Strength', 1e-10, granularity)
            self.world = world
            worldSize = np.array([world.xLength/granularity, world.yLength/granularity, world.zLength/granularity], dtype=int)
            self.values  = np.full(worldSize, self.steadyStateValue)
            self.world.addField(self)
            hotMap = np.array([[0.3333,         0,         0],
                                  [0.6667,         0,         0],
                                  [1.0000,         0,         0],      
                                  [1.0000,    0.3333,         0],
                                  [1.0000,    0.6667,         0],
                                  [1.0000,    1.0000,         0],
                                  [1.0000,    1.0000,    0.2500],
                                  [1.0000,    1.0000,    0.5000],
                                  [1.0000,    1.0000,    0.7500],
                                  [1.0000,    1.0000,    1.0000]])
            self.heatMapValues = np.array(hotMap*255, dtype='u1')
            self.maxValue = self.minValue = self.steadyStateValue
            self.setupDraw()

        def update(self):
            super(RF24Strength, self).update()
            # assign colors to points
            colors = vtk.vtkUnsignedCharArray()
            colors.SetNumberOfComponents(3)
            colors.SetName('Colors')
            for v in np.nditer(self.values):
                #choose a random color for testing
                c = choice(self.heatMapValues)
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
            idx = (v - self.minValue)/(self.maxValue-self.minValue)
            idx = int(idx*len(self.heatMapValues))
            return self.heatMapValues[idx]



class MobileRFObject(MobileObject, FieldObject):
    def __init__(self, **kwargs):
        super(MobileRFObject, self).__init__(**kwargs)
        sz = kwargs.get('size', [0,0,0])
        self.size = sz
        self.boundaryStart = (self.pos.x-self.size[0]/2, self.pos.y-self.size[1]/2, self.pos.z-self.size[2]/2)
        self.boundaryEnd = (self.pos.x+self.size[0]/2, self.pos.y+self.size[1]/2, self.pos.z+self.size[2]/2)
        self.setupDraw()
        
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
        self.actor.GetProperty().SetColor((0,0,1.0))

    def influencingRegion(self):
        """ Returns two points that define a bounding box for the direct influence of the object"""
        #TODO: needs a much clearer name
        return [self.boundaryStart, self.boundaryEnd]

    def influencedByRegion(self):
        """ Returns two points to define a bounding box for field values needed to update the object"""
        # let's only care about field value at our center, a single point
        return [self.pos, self.pos]
    
    def transformFieldValueAtPoint(oldVal, pt):
        """ Modify the field value at the point (add, subtract) if needed """
        return oldVal

    def update(self):
        self.position_update()
        self.actor.SetPosition(*self.pos)
        # use influence of field

class DrawingWorld(World):
    def __init__(self, xLength, yLength, zLength):
        super(DrawingWorld, self).__init__(xLength, yLength, zLength)
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.SetSize(800,600)
        self.renderWindow.AddRenderer(self.renderer)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renderWindow)
        

        self.startTime = time()

    def startDrawing(self):
        self.iren.Initialize()

        self.iren.AddObserver('TimerEvent', self.update)
        self.iren.CreateRepeatingTimer(100)

        self.iren.Start()

    def addActor(self, a):
        self.renderer.AddActor(a)

    def update(self, event, obj):
        super(DrawingWorld, self).update()
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

w.registerToField(m1, 'RFStrength')
w.startDrawing()
