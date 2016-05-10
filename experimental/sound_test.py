from world import World, DrawingWorld
from mobile_object import MobileObject
from field import SphereField, FieldObject, FieldInfluence, PlaneReflection
from time import time
import numpy as np
import vtk

from random import random

class SoundIntensity(SphereField):
    """ TODO: true intensity depends on the phase as well as mag (RMS?) """
    def __init__(self, world):
        super(SoundIntensity, self).__init__('Sound', [330.0, 0.05])
        self.world = world
        self.world.addField(self)

        self.maxValue = self.minValue = self.stopValue
        self.sphereActors = []

        self.freq = 650.0 #Hz - wavelength = 1.1m
        self.wavelength = self.spread[0] / self.freq

    def createSphereActor(self, s):
        """ given the FieldInfluence sphere, generate a vtk actor """
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*s.center)
        sphere.SetRadius(s.r)
        sphere.SetPhiResolution(15)
        sphere.SetThetaResolution(15)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(0.33333)

        return actor

    def reflectSphereIfNeeded(self, s):
        # let's only reflect off +- x for now
        firstReflect = PlaneReflection.reflectSphereFieldOffPlane(s, 0, -self.world.xLength/2)
        secondReflect = PlaneReflection.reflectSphereFieldOffPlane(s, 0, self.world.xLength/2)

        together = list(set(firstReflect+secondReflect))

        return together
        

    def stepFieldSphere(self, s, dt):
        mag, phase = s.mag
        newMag = mag * np.exp(-dt / self.spread[1])

        if newMag > self.stopValue:
            newR = s.r + self.spread[0] * dt
            currPhase = 2 * np.pi * newR / self.wavelength 

            return FieldInfluence(s.center, newR, (newMag, currPhase), s.reflectFrom)
        else:
            return None
       
    def update(self, dt):
        # remove all spheres - later we will do better
        for a in self.sphereActors:
            self.world.removeActor(a)

        self.sphereActors = []
        super(SoundIntensity, self).update(dt)

        allMags, allPhases = zip(*[s.mag for s in self.sphereList])
        logValues = np.log(allMags)

        self.maxValue = max(logValues)
        self.minValue = min(logValues)
        
        for i in range(len(logValues)):
            a = self.createSphereActor(self.sphereList[i])
            s = self.getHueForPhase(allPhases[i])
            h = self.getSaturationForValue(logValues[i])
            v = 1.0

            color = vtk.vtkMath.HSVToRGB(h,s,v)

            a.GetProperty().SetColor(*color)
            self.sphereActors.append(a)
            self.world.addActor(a)
        
    def mapValue(self, v, minVal, maxVal):
        if (maxVal == minVal):
            m = 0
        else:
            m = (v - minVal) / (maxVal - minVal)
        return m

    def getHueForPhase(self, phase):
        ''' phase must be given in radians '''
        sinP = np.sin(phase)
        hueValue = (sinP + 1) / 2

        return hueValue

    def getSaturationForValue(self, v):
        return self.mapValue(v, self.minValue, self.maxValue)

    def getHeatMapColor(self, v):
        if (self.maxValue == self.minValue):
            idx = 0.5
        else:
            idx = (v - self.minValue) / (self.maxValue - self.minValue)
        idx = int(idx * (len(self.heatMapValues) - 1))
        return self.heatMapValues[idx]

class SoundIntensityDots(SoundIntensity):
    def __init__(self, world, granularity):
        super(SoundIntensityDots, self).__init__(world)
        worldSize = np.array([world.xLength / granularity, world.yLength / granularity, world.zLength / granularity], dtype=int)
        self.gran = granularity
        self.defaultValue = 1e-10 + 0j
        self.values = np.full(worldSize, self.defaultValue, dtype=complex)
        self.heatMapValues = np.array([[36,    0,    0],
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

        self.setupDrawing(worldSize)
        self.world.addActor(self.actor)

    def setupDrawing(self, valuesShape):
        p = vtk.vtkPoints()
        v = vtk.vtkCellArray()

        s = self.values.shape[0:3]
        for x in range(s[0]):
            px = x * self.gran - self.world.xLength / 2
            for y in range(s[1]):
                py = y * self.gran - self.world.yLength / 2
                for z in range(s[2]):
                    pz = z * self.gran - self.world.zLength / 2
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
        props.SetPointSize(self.gran * 2)
        props.SetOpacity(0.1)

    def updateValues(self):
        originOffset = np.array([self.world.xLength / 2, self.world.yLength / 2, self.world.zLength / 2])
        originOffset += self.gran
        # for each sphere, accumulate its values into the world field strength
        # values at each point
        # start with cube approximations, and refine later
        # no reflections yet
        # TODO: is it faster to go point by point and find included circles?
        self.values.fill(self.defaultValue)

        s = self.values.shape

        for sph in self.sphereList:
            # TODO: do this in one array operation
            c = sph.center
            startX = max((c[0] - sph.r + originOffset[0]) / self.gran, 0)
            endX = min((c[0] + sph.r + originOffset[0]) / self.gran, s[0] - 1)
            startY = max((c[1] - sph.r + originOffset[1]) / self.gran, 0)
            endY = min((c[1] + sph.r + originOffset[1]) / self.gran, s[1] - 1)
            startZ = max((c[2] - sph.r + originOffset[2]) / self.gran, 0)
            endZ = min((c[2] + sph.r + originOffset[2]) / self.gran, s[2] - 1)

            sX = int(startX)
            eX = int(endX) + 1
            sY = int(startY)
            eY = int(endY) + 1
            sZ = int(startZ)
            eZ = int(endZ) + 1

            complexVal = sph.mag[0] * np.exp(1j * sph.mag[1])

            self.values[sX:eX, sY:eY, sZ:eZ] += complexVal
        
            
        allMags = (np.abs(np.real(self.values) + 1e-10)).flat
        allPhases = np.sin(np.angle(self.values)).flat

        logValues = np.log(allMags)
        minValue = min(logValues)
        maxValue = max(logValues)

        # assign colors to points
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(4)
        colors.SetName('Colors')
        for i in range(len(allMags)):
            #r,g,b = self.getHeatMapColor(logValues[i])
            #h = self.mapValue(allPhases[i], -1, 1) / 2
            #s = 1.0
            #v = 1.0
            h = 0.5
            a = self.mapValue(logValues[i], minValue, maxValue)
            s = a
            v = 1
            r,g,b = [int(c * 255) for c in vtk.vtkMath.HSVToRGB(h,s,v)]
            a = int(a*255)
            colors.InsertNextTuple4(r,g,b,a)

        self.pointData.GetPointData().SetScalars(colors)
        self.pointData.GetPointData().SetActiveScalars('Colors')
        self.pointData.Modified()

    def update(self, dt):
        super(SoundIntensity, self).update(dt)
        self.updateValues()




class MobileSoundObject(MobileObject, FieldObject):
    def __init__(self, **kwargs):
        super(MobileSoundObject, self).__init__(**kwargs)
        sz = kwargs.get('size', [0,0,0])
        self.size = sz
     
        self.setupDraw()
        self.emissionStrength = 5
        
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

    def getRadiatedValue(self):
        return (self.emissionStrength, 0)

    def update(self, dt):
        self.position_update(dt)
   
        self.actor.SetPosition(*self.pos)
        # use influence of field
w = DrawingWorld(200,200, 100, 0.005)
f = SoundIntensity(w)
#f = SoundIntensityDots(w, 5)
for i in range(2):
    m = MobileSoundObject(world=w, name="obj" + str(i), size=[10,10,10])
    w.addActor(m.actor)
    w.registerToField(m, 'Sound')

#m1 = MobileRFObject(world=w, name="zippy1", size=[10,10,10])
#m2 = MobileRFObject(world=w, name="zippy2", size=[10,10,10])

#w.addActor(m1.actor)
#w.addActor(m2.actor)

#w.registerToField(m1, 'RF24Strength')
#w.registerToField(m2, 'RF24Strength')
w.startDrawing()