from ode_objects import *
import ode
import visual as v
from operator import eq
import logging
import time

class Vpy_Visualization():
    def __init__(self, physicalEnvironment):
        self.logger = logging.getLogger(name='Quadsim.Visualizer')
        self.physEnv = physicalEnvironment
        self.obj = set()
        self.simFrames = 0
        self.objUpdates = 0

  
    def updateLabel(self):
        now = time.time()

        

    def create(self):
        space = self.physEnv.space
        for i in range(space.getNumGeoms()):
            geom = space.getGeom(i)
            self.addGeom(geom)

    def update(self, dt):
        for obj in self.obj:
            obj.update()
            #self.objUpdates +=1
        self.simFrames +=1 

    def getGraphics(self, geom):
        for o in self.obj:
            if eq(o.geom, geom):
                return o.src

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

            
