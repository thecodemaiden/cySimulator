import ode
from numpy import sqrt, array, arctan2, arcsin, cos, sum, arccos
from numpy.linalg import norm
import logging
from sensors import SemanticRadio, Accelerometer
from object_types import PhysicalObject
from time import time 

RADIO_ADDR=0x7E7E7E7EL
RADIO_CHAN=17

class Quadcopter(PhysicalObject):
    def __init__(self, params):
        environment = params['environment']
        super(Quadcopter, self).__init__(environment)
        self.logger = logging.getLogger(name='Quadsim.Quadcopter')
        #self.logger.setLevel(logging.DEBUG)
        self.sensors = {}

        getFloatParam = lambda x: float(params[x])

        armLength = getFloatParam('armLength')
        bodyLength = getFloatParam('centralBodyRadius')
        bodyHeight = getFloatParam('centralBodyHeight')
        motorMass = getFloatParam('motorMass')
        bodyMass = getFloatParam('bodyMass')

        ptc = getFloatParam('propellerThrustCoefficient')
        mdc = getFloatParam('motorDragCoefficient')
        afc = getFloatParam('airFrictionCoefficient')
        maxW = getFloatParam('maxPropW')

        ms = self.environment.massScale
        ls = self.environment.lengthScale
        fs = self.environment.forceScale

        self.propellerThrustCoefficient = ptc*fs
        self.motorDragCoefficient = mdc*fs
        self.airFrictionCoefficient = afc*fs

        self.maxPropellerW = maxW*fs

        self.totalMass = (bodyMass + 4*motorMass)*ms
       
        self.bodyLength = ls*float(bodyLength)
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

        self.time = 0

        self.name = "Quad1"
        self.motorW = [0,0,0,0]

        #self.makePhysicsBody()
        self.makeCrossBody()

        #attach an angular motor joint to the quadcopter
        self.aMotor = ode.AMotor(self.environment.world)
        self.aMotor.setNumAxes(3)
        self.aMotor.setMode(ode.AMotorEuler)
        self.aMotor.attach(self.physicsBody, None)
        self.aMotor.setAxis(0, 1, [1, 0, 0])
        self.aMotor.setAxis(2, 2, [0, 0, 1])

        r = SemanticRadio(self, {'address':RADIO_ADDR, 'channel':RADIO_CHAN})
        a = Accelerometer(self, {})
        self.addSensor('radio', r)
        self.addSensor('acc', a)

        self.moved = False

        #self.environment.addObject(self)
        self.pid = PidController(2, 0, 0)
        self.pid.target = [0.1,0.0,0.0]

    def addSensor(self, name, s):
        self.sensors[name] = s

    def setPosition(self, pos):
        x,y,z = [self.environment.lengthScale*c for c in pos]
        self.physicsBody.setPosition((x,y,z))

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
        self.physicsBody = mainBody

    def calculateThrust(self):
        return [0, sum(array(self.motorW))*self.propellerThrustCoefficient, 0]

    def calculateTorques(self):
        # roll, pitch, yaw
        return [self.armLength * self.propellerThrustCoefficient * (self.motorW[0] - self.motorW[2]),
                self.motorDragCoefficient * (-self.motorW[0] + self.motorW[1] - self.motorW[2] + self.motorW[3]),
                self.armLength * self.propellerThrustCoefficient * (self.motorW[1] - self.motorW[3])] 

    def pidOutputToMotors(self, err, total):
        # shamelessly ripped from MATLAB code
        inertia = self.physicsBody.getMass().I
        e1 = err[0]; e2 = err[1]; e3 = err[2]; 
        Ix = inertia[0][0]; Iy = inertia[1][1]; Iz = inertia[2][2]
        k = self.propellerThrustCoefficient
        L = self.armLength
        b = self.motorDragCoefficient

        each = total/4.0

        if each > self.maxPropellerW:
            each = self.maxPropellerW
        if each < 0:
            each = 0
   
        motorVals = [0,0,0,0]
        motorVals[0] = each -(-2 * b * e1 * Ix + e3 * Iz * k * L)/(4 * b * k * L);
        motorVals[1] = each + e3 * Iz/(4 * b) + (e2 * Iy)/(2 * k * L);
        motorVals[2] = each -(2 * b * e1 * Ix + e3 * Iz * k * L)/(4 * b * k * L);
        motorVals[3] = each + e3 * Iz/(4 * b) - (e2 * Iy)/(2 * k * L);

        return motorVals

    def totalThrustNeeded(self):
        R = self.physicsBody.getRotation()

        r  = arctan2(R[7], R[8]);     #phi
        y = arcsin(-R[6]);            #theta
        p   = arctan2(R[3], R[0]);    #psi

        theta = array([r,p,y])
        total = self.totalMass*-self.environment.world.getGravity()[1]*self.environment.forceScale
        total = total/self.propellerThrustCoefficient
        total = total/(cos(r)*cos(p))

        return total


    def update(self,dt):

        for dv in self.sensors.values():
            dv.update(dt)

        r = self.sensors['radio']
        # all PID and radio stuff will move to programs
        if self.time % 2.5 < dt:
            r.writePacket(RADIO_ADDR, RADIO_CHAN, "TEST")

        pid_error = self.pid.update(self, dt)
        thrust_adj = self.pidOutputToMotors(pid_error, self.totalThrustNeeded())
        self.motorW = thrust_adj

        # apply thrust and yaw torque at each prop
        thrust = self.calculateThrust()
        torque = self.calculateTorques()

        self.physicsBody.addRelForce(thrust)
        self.aMotor.addTorques(*torque)
        
        # finally, the air drag force - turns out we need it to hover!
        v = self.physicsBody.getLinearVel()
        vMag = norm(v)
        airFriction = (array(v)*-self.airFrictionCoefficient*vMag)
        self.physicsBody.addForce(airFriction)

        v = self.sensors['acc'].getValue()

        self.logger.info('{}.acc x: {}\ty: {}\tz: {}'.format(self.name, *v))
       

    
class PidController(object):
    def __init__(self, Kp, Ki, Kd):
        self.target = array([0.0,0.0,0.0])
        self.kp = Kp
        self.ki = Ki
        self.kd = Kd

        self.integral = array([0.0,0.0,0.0])
        self.lastError = array([0.0,0.0,0.0])

    def update(self, copter, dt):
       
        R = copter.physicsBody.getRotation()

        r  = arctan2(R[7], R[8]);     #phi
        y = arcsin(-R[6]);            #theta
        p   = arctan2(R[3], R[0]);    #psi

        theta = array([r,p,y])
        #get thetadot later...
        #thetadot = array(copter.getAngularVelocity())
        fs = copter.environment.forceScale

        nowError = self.target - theta
        dError = (nowError - self.lastError)/dt

        err = self.kp * nowError + self.ki * self.integral + self.kd * dError

        self.integral += dt*nowError
        self.lastError = nowError

        return err

class SimplePid(object):
    def __init__(self, kP, kI, kD, i_limit=1):
        self.kp = float(kP)
        self.ki = float(kI)
        self.kd = float(kD)
        self.i_limit_hi = float(i_limit)
        self.i_limit_lo = float(-i_limit)
        self.target = 0.0
        self.reset()

    def reset(self):
        #self.error = 0
        self.last_error = 0.0
        self.integral = 0.0

    def update(self, measured, dt):
        error = self.target - measured
        self.integral += error*dt
        self.integral = max(self.i_limit_lo, min(self.i_limit_hi, self.integral))
        d = (error - self.last_error)/dt
        self.last_error = error
        output = error*self.kp + self.integral*self.ki + d*self.kd

        return output

class PidRateAtt(object):
    def __init__(self):
        self.rollRatePid = SimplePid(250.0, 500, 2.5, 33.3)
        self.pitchRatePid = SimplePid(250.0, 500, 2.5, 33.3)
        self.yawRatePid = SimplePid(70.0, 16.7, 0, 166.7)

        self.rollPid = SimplePid(10, 4.0, 0, 20.)
        self.pitchPid = SimplePid(10, 4.0, 0, 20.)
        self.yawPid = SimplePid(10, 1.0, 0.35, 360)

        self.rollOutput = 0.0
        self.pitchOutput = 0.0
        self.yawOutput = 0.0

        self.target = [0.,0.,0.]

        self.thrustTarget = 0.0
        

    def update(self, copter, dt):
        """ Targets should be a sequence of (roll, pitch, yaw, thrust) """
        R = copter.physicsBody.getRotation()

        r  = arctan2(R[7], R[8]);     #phi
        y = arcsin(-R[6]);            #theta
        p   = arctan2(R[3], R[0]);    #psi

        self.rollPid.target = self.target[0]
        self.pitchPid.target = self.target[1]
        self.yawPid.target = self.target[2]

        #self.thrustTarget = targets[3]

        rollRate = self.rollPid.update(r, dt)
        pitchRate = self.pitchPid.update(p, dt)
        yawRate = self.yawPid.update(y, dt)

        self.rollRatePid.target = rollRate
        self.pitchRatePid.target = pitchRate
        self.yawRatePid.target = yawRate

        wr = copter.aMotor.getAngleRate(0)
        wy = copter.aMotor.getAngleRate(1)
        wp = copter.aMotor.getAngleRate(2)
         

        self.rollOutput = self.rollRatePid.update(wr, dt)
        self.pitchOutput = self.pitchRatePid.update(wp, dt)
        self.yawOutput = self.yawRatePid.update(wy, dt)

        return self.rollOutput, self.pitchOutput, self.yawOutput