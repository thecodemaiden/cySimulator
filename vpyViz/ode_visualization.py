from ode_objects import *
import ode
import visual as v
from operator import eq
import logging

class Vpy_Visualization():
    def __init__(self, dt):
        self.logger = logging.getLogger(name='Quadsim.Environment')

        self.world = ode.World()
        self.space = ode.Space()
        self.dt = dt
        self.obj = set()
        self.fieldList = {}
        self.contactGroup = ode.JointGroup()
        self.lengthScale = 1.0
        self.massScale = 1.0
        self.forceScale = self.lengthScale*self.massScale

    def addField(self, fieldName, f):
        self.fieldList[fieldName] = {'field':f, 'display':{}}

    def addFieldObject(self, fieldName, o):
        # TODO: error behavior
        fieldInfo = self.fieldList[fieldName]
        fieldInfo['field'].addObject(o)

    def create(self):
        for i in range(self.space.getNumGeoms()):
            geom = self.space.getGeom(i)
            self.addGeom(geom)

    def step(self, dt):
        self.space.collide(None, self.near_callback)
        self.world.quickStep(dt)
        self.contactGroup.empty()


    def update(self):
        for obj in self.obj:
            obj.update()
        self.step(self.dt)

    def getGraphics(self, geom):
        for o in self.obj:
            if eq(o.geom, geom):
                return o.src

    def near_callback(self, args, geom1, geom2):
        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # Create contact joints
        for c in contacts:
            c.setBounce(0.7)
            c.setMu(500)
            j = ode.ContactJoint(self.world, self.contactGroup, c)
            j.attach(geom1.getBody(), geom2.getBody())


    def extractObj(self, geom, ident):
        obj = None
        # Box
        if type(geom) == ode.GeomBox:
            obj = Vpy_Box(geom, ident)
        # Sphere
        elif type(geom) == ode.GeomSphere:
            obj = Vpy_Sphere(geom, ident)
        # Plane
        elif type(geom) == ode.GeomPlane:
            obj = Vpy_Plane(geom, ident)
        # Ray
        elif type(geom) == ode.GeomRay:
            obj = Vpy_Ray(geom, ident)
        # TriMesh
        elif type(geom) == ode.GeomTriMesh:
            obj = Vpy_TriMesh(geom, ident)
        # Cylinder
        elif type(geom) == ode.GeomCylinder:
            obj = Vpy_Cylinder(geom, ident)
        # Capsule
        elif type(geom) == ode.GeomCapsule:
            obj = Vpy_Capsule(geom, ident)
        # CappedCylinder
        elif type(geom) == GeomCCylinder:
            obj = Vpy_Capsule(geom, ident)
        elif type(geom) == ode.GeomTransform:
            obj = self.extractObj(geom.getGeom(), ident)
            obj = Vpy_Transform(geom, obj, ident)

        return obj

    def addGeom(self, geom, ident=None):
        obj = self.extractObj(geom, ident)
        obj.update()
        if obj:
            self.obj.add(obj)

    def runloop(self):
        while 1:
            v.rate(100)
            if v.scene.mouse.events:
                pass
            
