from vtk import *
import ode
from numpy import sqrt
import logging

class Quadcopter(object):
    def __init__(self, armLength, bodyLength, bodyHeight, motorMass, bodyMass, environment):
        super(Quadcopter, self).__init__()
        self.logger = logging.getLogger(name='Quadsim.Quadcopter')
        self.logger.setLevel(logging.DEBUG)

        self.propellerThrustCoefficient = 1e-4
        self.motorDragCoefficient = 1e-7
        self.airFrictionCoefficient = 0.25

        self.armLength = armLength
        self.bodyLength = float(bodyLength) / 2.0
        self.bodyHeight = bodyHeight
        self.motorHeight = 1.1*bodyHeight
        self.motorRadius = float(bodyHeight) / 2.0
        offset = self.armLength + float(self.bodyLength) / 2.0
        self.armOffsets = [(0, 0, offset),
                  (offset, 0, 0),
                  (0, 0, -offset),
                  (-offset, 0, 0)]

        self.armDragDirections = [(1, 0, 0),
                                  (0, 0, 1),
                                  (-1, 0, 0),
                                  (0, 0, -1)]

        self.motorMass = motorMass
        self.bodyMass = bodyMass

        self.environment = environment
        self.name = "Quad1"
        x = 198.05
        self.motorW = [x,x,x,x]

        self.makePhysicsBody()

    def makePhysicsBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space

        self.geomList = []

        offset = self.armLength + float(self.bodyLength) / 2.0
        

        mainBody = ode.Body(physicsWorld)
        bodyMass = ode.Mass()
        bodyMass.setCylinderTotal(self.bodyMass, 3, self.bodyLength, self.bodyHeight)
        
        geom = ode.GeomCylinder(None, self.bodyLength, self.bodyHeight)
        #geom.setBody(mainBody)
        gt = ode.GeomTransform(space)
        gt.setBody(mainBody)
        gt.setGeom(geom)
        geom.setRotation((1,0,0,0,0,-1,0,1,0))
        self.geomList.append(gt)

        for i in range(4):
            mass = ode.Mass()
            mass.setCylinderTotal(self.motorMass,3, self.motorRadius, self.motorHeight)
            mass.translate(self.armOffsets[i])
            bodyMass.add(mass)

            g = ode.GeomCylinder(None, self.motorRadius, self.motorHeight)
            gt = ode.GeomTransform(space)
            gt.setGeom(g)
            gt.setBody(mainBody)

            g.setPosition(self.armOffsets[i])
            g.setRotation((1,0,0,0,0,-1,0,1,0))
            self.geomList += [gt]

        geom.setRotation((1,0,0,0,0,-1,0,1,0))
        mainBody.setMass(bodyMass)
        self.centerBody = mainBody

   

    def calculatePropDrag(self):
        drag = [0,0,0,0]
        for i in range(4):
            drag[i] = self.motorW[i]*self.motorW[i]*self.motorDragCoefficient
        return drag

    def calculatePropThrust(self):
        thrust = [0,0,0,0]
        for i in range(4):
            thrust[i] = self.motorW[i]*self.motorW[i]*self.propellerThrustCoefficient
        return thrust

    def update(self):
        # apply thrust and torque at each prop
        dr = self.calculatePropDrag()
        th = self.calculatePropThrust()
        for i in range(4):
            dragForce = [0,0,0,0]# [dr[i]*d for d in self.armDragDirections[i]]
            thrust = [th[i]*d for d in (0,1,0)]
            totalForces = (dragForce[0]+thrust[0], dragForce[1]+thrust[1], dragForce[2]+thrust[2])
            self.centerBody.addRelForceAtRelPos(totalForces, self.armOffsets[i])
        self.logger.debug("Torque on qc: %5.2f, %5.2f, %5.2f" % self.centerBody.getTorque())
        self.logger.debug("Force on qc: %5.2f, %5.2f, %5.2f" % self.centerBody.getForce())


        

