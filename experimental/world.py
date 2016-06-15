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

    def update(self,dt):
        for f in self.fieldList:
            f.update(dt)
        for o in self.entityList:
            o.update(dt)

import vtk
class DrawingWorld(World):
    def __init__(self, xLength, yLength, zLength, dt=0.1):
        super(DrawingWorld, self).__init__(xLength, yLength, zLength)
        self.renderer = vtk.vtkRenderer()
        self.renderWindow = vtk.vtkRenderWindow()
        self.renderWindow.SetSize(800,600)
        self.renderWindow.AddRenderer(self.renderer)
        self.iren = vtk.vtkRenderWindowInteractor()
        self.iren.SetRenderWindow(self.renderWindow)

        #self.actor = vtk.vtkCubeAxesActor()
        boundingBox = vtk.vtkCubeSource()
        boundingBox.SetXLength(xLength)
        boundingBox.SetYLength(yLength)
        boundingBox.SetZLength(zLength)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(boundingBox.GetOutputPort())

        self.actor = vtk.vtkActor()
        self.actor.SetMapper(mapper)
        self.actor.GetProperty().SetRepresentationToWireframe()
        

        self.camera = self.renderer.GetActiveCamera()
        self.camera.SetFocalPoint((0,0,0))
        self.camera.SetPosition((0, 0, 300))
        self.renderer.SetActiveCamera(self.camera)
        #self.actor.SetCamera(self.camera)
        #self.actor.SetBounds(-xLength/2, xLength/2, -yLength/2, yLength/2, -zLength/2, zLength/2)
        #self.actor.DrawXGridlinesOn()
        #self.actor.DrawYGridlinesOn()
        #self.actor.DrawZGridlinesOn()

        self.renderer.AddActor(self.actor)

        self.dt = dt

    def startDrawing(self):
        self.iren.Initialize()

        self.iren.AddObserver('TimerEvent', self.update)
        self.iren.CreateRepeatingTimer(100)

        self.iren.Start()

    def addActor(self, a):
        self.renderer.AddActor(a)

    def removeActor(self, a):
        self.renderer.RemoveActor(a)

    def update(self, event, obj):
        super(DrawingWorld, self).update(self.dt)
        self.renderWindow.Render()
        #if time() > self.startTime + 10:
        #   self.iren.TerminateApp()

