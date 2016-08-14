from ode import AMotor, AMotorEuler

class PhysicalObject(object):
    """Common methods for objects that are part of the physical simulation"""
    def __init__(self, environment):
        self.environment = environment

    def updatePhysics(self, dt):
        pass

    def onVisualizationStart(self):
        pass

class ComputationalObject(object):
    """ Common methods for objects that are part of the computational simulation """
    def __init__(self, environment):
        self.environment = environment
        self.deviceTask = None

    def updateComputation(self, dt):
        # TODO: use the dt
        if self.deviceTask is not None:
            self.deviceTask.tick(dt)

class Device(ComputationalObject, PhysicalObject):
    def __init__(self, params):                
        environment = params['environment']
        super(Device, self).__init__(environment)
        self.sensors = {}
        self.name = "Device"
        self.applyParameters(params)
        self.makePhysicsBody()
        self.attachOrientationJoint()

    def makePhysicsBody(self):
        self.physicsBody = None # MUST OVERRIDE
        raise RuntimeError('New devices must define a physical body!')

    def attachOrientationJoint(self):
        # please leave this alone!!
        self.orientationMotor = AMotor(self.environment.world)
        self.orientationMotor.setNumAxes(3)
        self.orientationMotor.setMode(AMotorEuler)
        self.orientationMotor.attach(self.physicsBody, None)
        self.orientationMotor.setAxis(0, 1, [1, 0, 0])
        self.orientationMotor.setAxis(2, 2, [0, 0, 1])

    def applyParameters(self, params):
        pass

    def addSensor(self, name, s):
        self.sensors[name] = s

    def getSensor(self, name):
        return self.sensors.get(name, None)

    def setPosition(self, pos):
        x,y,z = [self.environment.lengthScale*c for c in pos]
        self.physicsBody.setPosition((x,y,z))

