from ode import AMotor, AMotorEuler

class _Base(object):
    def __init__(self, *args):
        pass

class PhysicalObject(_Base):
    """Common methods for objects that are part of the physical simulation"""
    def __init__(self, environment):
        super(PhysicalObject, self).__init__(environment)
        self.environment = environment
        self.logger = None
        self.color = (1.0,1.0,1.0)
        self.geomList = []
        self.makePhysicsBody()
        self.attachOrientationJoint()

    def attachOrientationJoint(self):
        # please leave this alone!! It reports ground truth orientation of the physical object
        self.orientationMotor = AMotor(self.environment.world)
        self.orientationMotor.setNumAxes(3)
        self.orientationMotor.setMode(AMotorEuler)
        self.orientationMotor.attach(self.physicsBody, None)
        self.orientationMotor.setAxis(0, 1, [1, 0, 0])
        self.orientationMotor.setAxis(2, 2, [0, 0, 1])

    def makePhysicsBody(self):
        self.physicsBody = None # MUST OVERRIDE
        raise RuntimeError('Physical objects must define a physical body!')


    def updatePhysics(self, dt):
        pass

    def onVisualizationStart(self):
        for geom in self.geomList:
            g = self.environment.visualizer.getGraphics(geom)
            g.color = self.color

    def setPosition(self, pos):
        x,y,z = [self.environment.lengthScale*c for c in pos]
        self.physicsBody.setPosition((x,y,z))

    def getPosition(self):
        return self.physicsBody.getPosition()

class ComputationalObject(_Base):
    """ Common methods for objects that are part of the computational simulation """
    def __init__(self, environment):
        super(ComputationalObject, self).__init__(environment)
        self.environment = environment
        self.deviceTask = None
        self.logger = None

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
        self.time = 0
        self.applyParameters(params)

    def applyParameters(self, params):
        pass

    def addSensor(self, name, s):
        self.sensors[name] = s

    def getSensor(self, name):
        return self.sensors.get(name, None)


