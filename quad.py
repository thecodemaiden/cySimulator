from vtk import *
import ode
from numpy import sqrt, array
from numpy.linalg import norm
import logging

class Quadcopter(object):
    def __init__(self, armLength, bodyLength, bodyHeight, motorMass, bodyMass, environment):
        super(Quadcopter, self).__init__()
        self.logger = logging.getLogger(name='Quadsim.Quadcopter')
        self.logger.setLevel(logging.DEBUG)

        self.environment = environment
        ms = self.environment.massScale
        ls = self.environment.lengthScale
        fs = self.environment.forceScale


        self.propellerThrustCoefficient = 1e-4*fs
        self.motorDragCoefficient = 1e-7*fs
        self.airFrictionCoefficient = 0.25*fs

        self.armLength = armLength*ls
        self.bodyLength = ls*float(bodyLength) / 2.0
        self.bodyHeight = bodyHeight*ls
        self.motorHeight = 1.2*bodyHeight*ls
        self.motorRadius = ls*float(bodyHeight) / 2.0
        offset = self.armLength + float(self.bodyLength) / 2.0
        self.armOffsets = [(0, 0, offset),
                  (offset, 0, 0),
                  (0, 0, -offset),
                  (-offset, 0, 0)]

        self.armDragDirections = [(1, 0, 0),
                                  (0, 0, 1),
                                  (-1, 0, 0),
                                  (0, 0, -1)]

        self.motorMass = motorMass*ms
        self.bodyMass = bodyMass*ms

        self.name = "Quad1"
        x = 198.05
        self.motorW = [0,0,0,0]#[x/sqrt(2),x/sqrt(2),x/sqrt(2),x/sqrt(2)]

        self.makePhysicsBody()
        #self.environment.addObject(self)

    def onVisualizationStart(self):
        pass

    def makePhysicsBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space

        self.geomList = []

        offset = self.armLength + float(self.bodyLength) / 2.0

        mainBody = ode.Body(physicsWorld)
        bodyMass = ode.Mass()
        bodyMass.setCylinderTotal(self.bodyMass, 3, self.bodyLength, self.bodyHeight)
        
        geom = ode.GeomCylinder(space, self.bodyLength, self.bodyHeight)
        geom.setBody(mainBody)    
        geom.setOffsetRotation((1,0,0,0,0,-1,0,1,0))
        self.geomList.append(geom)

        for i in range(4):
            mass = ode.Mass()
            mass.setCylinderTotal(self.motorMass,3, self.motorRadius, self.motorHeight)
            mass.translate(self.armOffsets[i])
            bodyMass.add(mass)

            g = ode.GeomCylinder(space, self.motorRadius, self.motorHeight)
            g.setBody(mainBody)

            g.setOffsetPosition(self.armOffsets[i])
            g.setOffsetRotation((1,0,0,0,0,-1,0,1,0))

            self.geomList += [g]

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
            dragForce =  [dr[i]*d for d in self.armDragDirections[i]]
            thrust = [th[i]*d for d in (0,1,0)]
            totalForces = (dragForce[0]+thrust[0], dragForce[1]+thrust[1], dragForce[2]+thrust[2])
            self.centerBody.addRelForceAtRelPos(totalForces, self.armOffsets[i])
        
        # finally, the air drag force - turns out we need it to hover!
        v = self.centerBody.getLinearVel()
        vMag = norm(v)
        airFriction = (array(v)*-self.airFrictionCoefficient*vMag)
        self.centerBody.addForce(airFriction)
       


        

