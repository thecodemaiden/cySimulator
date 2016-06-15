from vtk import *

s = vtkSphereSource()
s.SetRadius(2)
p = vtkPlane()
p.SetOrigin(0,1,0) # y = 1, plane facing y direction
p.SetNormal(0,1,0)
p2 = vtkPlane()
p2.SetOrigin(1,0,0)
p2.SetNormal(1,0,0)

together = vtkImplicitBoolean()
together.AddFunction(p)
together.AddFunction(p2)
together.SetOperationToIntersection()


clipper = vtkClipPolyData()
clipper.SetInputConnection(s.GetOutputPort())
clipper.SetClipFunction(p)
clipper.Update()


polyData = clipper.GetOutput()

mapper = vtkPolyDataMapper()
mapper.SetInputConnection(clipper.GetOutputPort())
#mapper.SetInputConnection(s.GetOutputPort())

actor = vtkActor()
actor.SetMapper(mapper)

ren = vtkRenderer()
win = vtkRenderWindow()
win.AddRenderer(ren)
rwi = vtkRenderWindowInteractor()
rwi.SetRenderWindow(win)

ren.AddActor(actor)
ren.Render()
rwi.Start()



