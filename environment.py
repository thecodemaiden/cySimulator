import ode
import logging
from vtk import vtkCamera

from odeViz.ode_visualization import ODE_Visualization

class MyVisualization(ODE_Visualization):
    def __init__(self, world, space, env, dt):
        super(MyVisualization, self).__init__(world, space, dt)
        self.camera = vtkCamera()
        self.camera.SetFocalPoint((0,0,0))
        self.camera.SetPosition((0.5, 9.65078853769, 80.9784089121))
        self.ren.SetActiveCamera(self.camera)

        self.contactGroup = ode.JointGroup()
        self.environment = env

    def execute(self, caller, event):
        self.environment.update(self.dt)
        n = 2
        for i in range(n):
            self.space.collide(None, self.near_callback)
            self.step(self.dt/n)
            self.contactGroup.empty()
        self.update() # do not forget ...

    def near_callback(self, args, geom1, geom2):
        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # Create contact joints
        for c in contacts:
            c.setBounce(0.1)
            c.setMu(500)
            j = ode.ContactJoint(self.world, self.contactGroup, c)
            j.attach(geom1.getBody(), geom2.getBody())


class Environment(object):
    def __init__(self, dt=0.05, windowW=1024, windowH=768):
        super(Environment, self).__init__()
        self.world = ode.World()
        self.space = ode.Space()
        self.dt = dt;

        self.world.setGravity((0,-9.81,0))
        self.world.setCFM(1e-2)
        self.world.setERP(0.5) # seems to make the collision behavior more stable

        self.objectList = []

        self.logger = logging.getLogger(name='Quadsim.Environment')
        self.logger.setLevel(logging.DEBUG)

        groundY = -10
        
        self.floor = ode.GeomPlane(self.space, (0, 1, 0), groundY);

    def addObject(self, obj):
        self.objectList.append(obj)

    def start(self):
        self.sim = MyVisualization(self.world, self.space, self, self.dt)
        self.sim.GetProperty(self.floor).SetColor(1.,0,.5)
        self.sim.GetProperty(self.floor).SetRepresentationToWireframe()
        self.sim.start()

    def update(self, dt):
        for o in self.objectList:
            o.update()



