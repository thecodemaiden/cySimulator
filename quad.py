from vtk import *
import ode
from numpy import sqrt
import logging

class Quadcopter(object):
    def __init__(self, armLength, bodyLength, bodyHeight, motorMass, bodyMass, environment):
        super(Quadcopter, self).__init__()
        self.logger = logging.getLogger(name='Quadsim.Environment')
        self.logger.setLevel(logging.DEBUG)

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

        self.motorMass = motorMass
        self.bodyMass = bodyMass

        self.environment = environment
        self.name = "Quad1"

        self.makePhysicsBody()

    def makePhysicsBody(self):
       #self.makePhysicsWithJoints()
        self.makePhysicsOneBody()

    def makePhysicsOneBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space

        self.geomList = []

        offset = self.armLength + float(self.bodyLength) / 2.0
        tempOffsets = [(0, offset,0),
                  (offset, 0, 0),
                  (0,-offset,0),
                  (-offset, 0, 0)]

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

        self.centerBody = mainBody



     
    def makePhysicsWithJoints(self):
        physicsWorld = self.environment.world
        space = self.environment.space
      
        hubBody = ode.Body(physicsWorld)
        bodyMass = ode.Mass()
        bodyMass.setCylinderTotal(self.bodyMass, 3, self.bodyLength, self.bodyHeight)
        hubBody.setMass(bodyMass)

        geom = ode.GeomCylinder(space, self.bodyLength, self.bodyHeight)
        geom.setBody(hubBody)
        #geom.setQuaternion((sqrt(0.5),sqrt(0.5),0,0))
        geom.setRotation((1,0,0,0,0,-1,0,1,0))


        self.centerBody = hubBody
        self.centerGeom = geom

        # now we add the motors... fun :/
        self.motorInfo = []
        for i in range(4):
            body = ode.Body(physicsWorld)
            mass = ode.Mass()
            mass.setCylinderTotal(self.motorMass,3, self.motorRadius, self.motorHeight)
            body.setMass(mass)
            
            geom = ode.GeomCylinder(space, self.motorRadius, self.motorHeight)
            geom.setBody(body)
            #geom.setQuaternion((sqrt(0.5),sqrt(0.5),0,0))
            geom.setRotation((1,0,0,0,0,-1,0,1,0))

            geom.setPosition(self.armOffsets[i])

            # and the arm joints 
            #TODO: draw as lines
            j = ode.FixedJoint(physicsWorld)
            j.attach(body, hubBody)
            j.setFixed()

            self.motorInfo.append((body,geom, j))

    def update(self):
        # any internal physics updates
        pass

