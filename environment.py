import ode
import logging
from vtk import vtkCamera

from odeViz.ode_visualization import ODE_Visualization

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
        
        self.frametime = 1.0/60 #30 fps
        self.frameAccum = 0 # when this hits >= frametime, set to 0 and repaint

    def execute(self, caller, event):
        self.environment.update(self.dt)
        n = 2
        for i in range(n):
            self.space.collide(None, self.near_callback)
            self.step(self.dt/n)
            self.contactGroup.empty()
        if self.frameAccum >= self.frametime:
            self.update() # do not forget ...
            self.frameAccum = 0
        else:
            self.updateStatus()
        self.frameAccum += self.dt

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
        self.lengthScale = 10.0
        self.massScale = 10.0 # now a unit is 10g, not 1kg...
        self.forceScale = self.massScale*self.lengthScale

        self.dt = dt/self.lengthScale;


        self.world.setGravity((0,-9.81*self.forceScale,0))
        self.world.setCFM(1e-5)
        self.world.setERP(0.8) # seems to make the collision behavior more stable
        self.world.setContactSurfaceLayer(0.001)

        self.objectList = []

        self.logger = logging.getLogger(name='Quadsim.Environment')
        self.logger.setLevel(logging.DEBUG)

        groundY = -10
        
        #self.floor = ode.GeomPlane(self.space, (0, 1, 0), groundY);

    def getGeomVizProperty(self, g):
        return self.sim.GetProperty(g)


    def addObject(self, obj):
        # assumes body is already in our world, and collision geoms are in our space
        self.objectList.append(obj)

    def start(self):
        self.sim = MyVisualization(self.world, self.space, self, self.dt)
        #self.sim.GetProperty(self.floor).SetColor(1.,0,.5)
        for o in self.objectList:
            o.onVisualizationStart()
        self.sim.start()

    def update(self, dt):
        for o in self.objectList:
            o.update()



