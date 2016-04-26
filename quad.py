from vtk import *
import ode
from numpy import sqrt, array, arctan2, arcsin, cos, sum, arccos
from numpy.linalg import norm
import logging

from time import time 

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

        self.totalMass = (bodyMass + 4*motorMass)*ms
       
        self.bodyLength = ls*float(bodyLength) / 2.0
        self.armLength = armLength*ls + float(self.bodyLength)/2.0
        self.bodyHeight = bodyHeight*ls
        self.motorHeight = 1.2*bodyHeight*ls
        self.motorRadius = ls*float(bodyHeight) / 2.0
        self.armOffsets = [(0, 0, self.armLength),
                  (self.armLength, 0, 0),
                  (0, 0, -self.armLength),
                  (-self.armLength, 0, 0)]

        self.motorMass = motorMass*ms
        self.bodyMass = bodyMass*ms

        self.name = "Quad1"
        self.motorW = [0,0,0,0]

        #self.makePhysicsBody()
        self.makeCrossBody()
        self.startTime = None
        self.moved = False
        #self.environment.addObject(self)
        self.pid = PidController(30, 1, 0)

    def onVisualizationStart(self):
        pass

    def makeCrossBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space


        mainBody = ode.Body(physicsWorld)
        bodyMass = ode.Mass()
        totalMass = self.bodyMass+4*self.motorMass
        offset = self.armLength + float(self.bodyLength) / 2.0

        #one arm
        bodyMass.setBoxTotal(totalMass/2.0, offset, self.bodyHeight, self.motorRadius)
        # next arm
        armMass = ode.Mass()
        armMass.setBoxTotal(totalMass/2.0, self.motorRadius, self.bodyHeight, offset)
        bodyMass.add(armMass)

        firstArmGeom = ode.GeomBox(space, (offset, self.bodyHeight, self.motorRadius))
        secondArmGeom = ode.GeomBox(space, (self.motorRadius, self.bodyHeight, offset))

        mainBody.setMass(bodyMass)
        firstArmGeom.setBody(mainBody)
        secondArmGeom.setBody(mainBody)

        self.geomList = [firstArmGeom, secondArmGeom]
        self.centerBody = mainBody


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
        ''' unused... '''
        drag = [0,0,0,0]
        for i in range(4):
            drag[i] = self.motorW[i]*self.motorW[i]*self.motorDragCoefficient
            #drag[i] = self.motorW[i]*self.motorDragCoefficient
        return drag

    def calculatePropThrust(self):
        ''' unused... '''
        thrust = [0,0,0,0]
        for i in range(4):
            thrust[i] = self.motorW[i]*self.motorW[i]*self.propellerThrustCoefficient
        return thrust

    def calculateThrust(self):
        return [0, sum(array(self.motorW))*self.propellerThrustCoefficient, 0]

    def calculateTorques(self):
        return [self.armLength * self.propellerThrustCoefficient * (self.motorW[0] - self.motorW[2]),
                self.motorDragCoefficient * (self.motorW[0] - self.motorW[1] + self.motorW[2] - self.motorW[3]),
                self.armLength * self.propellerThrustCoefficient * (self.motorW[1] - self.motorW[3])] 

    def update(self,dt):
        if self.startTime is None:
            self.startTime = time()
        elif (time() > self.startTime + 10) and not self.moved:
                self.pid.target = array([0, 0., .0524])
                self.moved = True

        thrust_adj = self.pid.update(self, dt)
        x = 48000
        self.motorW = thrust_adj

        # apply thrust and yaw torque at each prop
        thrust = self.calculateThrust()
        torque = self.calculateTorques()

        self.centerBody.addRelForce(thrust)
        self.centerBody.addRelTorque(torque)
        
        # finally, the air drag force - turns out we need it to hover!
        v = self.centerBody.getLinearVel()
        vMag = norm(v)
        airFriction = (array(v)*-self.airFrictionCoefficient*vMag)
        self.centerBody.addForce(airFriction)
       


    
class PidController(object):
    def __init__(self, Kp, Ki, Kd):
        self.target = array([0.0,0.0,0.0])
        self.kp = Kp
        self.ki = Ki
        self.kd = Kd

        self.integral = array([0.0,0.0,0.0])
        self.lastError = array([0.0,0.0,0.0])

    def update(self, copter, dt):
       
        R = copter.centerBody.getRotation()

        r  = arctan2(R[7], R[8]);     #phi
        y = arcsin(-R[6]);            #theta
        p   = arctan2(R[3], R[0]);    #psi

        ''' 
        q = copter.centerBody.getQuaternion()
        r = arctan2(2*(q[0]*q[1] + q[2]*q[3]), 1 - 2*(q[1]*q[1] + q[2]*q[2]))
        p = arcsin(2*(q[0]*q[2] - q[3]*q[1]))
        y = arctan2(2*(q[0]*q[3] + q[1]*q[2]), 1 - 2*(q[2]*q[2] + q[3]*q[3]))
        '''

        theta = array([r,p,y])
        #get thetadot later...
        #thetadot = array(copter.getAngularVelocity())
        fs = copter.environment.forceScale

        # WTF is hapenning????
        #totalW2 = copter.totalMass * 9.81*fs/ (copter.propellerThrustCoefficient * cos(r) * cos(p))
        totalW2 = 48000*4

        nowError = self.target - theta
        dError = (nowError - self.lastError)/dt

        err = self.kp * nowError + self.ki * self.integral + self.kd * dError

        self.integral += dt*nowError
        self.lastError = nowError

        return self.err2inputs(copter, err, totalW2)

    def err2inputs(self, copter, err, total):
        # shamelessly ripped from MATLAB code
        inertia = copter.centerBody.getMass().I
        e1 = err[0]; e2 = err[1]; e3 = err[2]; 
        Ix = inertia[0][0]; Iz = inertia[1][1]; Iy = inertia[2][2]
        k = copter.propellerThrustCoefficient
        L = copter.armLength
        b = copter.motorDragCoefficient

        eachW2 = total/4
        each = eachW2

        motorVals = [0,0,0,0]
        motorVals[0] = each -(2 * b * e1 * Ix + e3 * Iz * k * L)/(4 * b * k * L);
        motorVals[1] = each + e3 * Iz/(4 * b) - (e2 * Iy)/(2 * k * L);
        motorVals[2] = each -(-2 * b * e1 * Ix + e3 * Iz * k * L)/(4 * b * k * L);
        motorVals[3] = each + e3 * Iz/(4 * b) + (e2 * Iy)/(2 * k * L);

        return (motorVals)


        
