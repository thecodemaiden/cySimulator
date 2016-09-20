import ode
from object_types import Device
from field_types import FieldObject
from random import gauss
from bisect import bisect_left
from sensors import Geophone

class FakeStepper(FieldObject, Device):
    """An object with no body that generates fake footstep vibrations"""
    def makePhysicsBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space

        mainBody = ode.Body(physicsWorld)
        mainBody.setKinematic()
       
        self.physicsBody = mainBody
        self.environment.addFieldObject('Vibration', self)

    def getRadiatedValues(self):
        if not self.stepMade:
            if self.lastT >= self.stepT:
                self.stepMade = True
                return (360, self.currentStep[1], self.stepT)
        return [(None, None, None)]

    def applyParameters(self, params):
        # time, step position, relative intensity
        posStr = params['stepPositions']
        posList = posStr.split(';')
        self.stepPositions = []
        for p in posList:
            p = [float(i) for i in p.split(',')]
            self.stepPositions.append(p)

        self.stepDt = float(params.get('stepDt', 1.0))
        self.stepTSigma = float(params.get('stepTSigma', 0.1))
        self.stepPSigma = float(params.get('stepPSigma', 0.1))
        self.currentStep = None
        self.stepMade  = False
        self.lastT = 0
        self.stepT = 0
        self.steps = {}
        self.prepareSteps()

    def updatePhysics(self, dt):
        self.lastT = self.environment.time
        allT = self.steps.keys()
        currTIdx = bisect_left(allT, self.lastT)
        # the value at currTIdx >= now
        lastStepT = self.stepT
        if lastStepT != self.stepT:
            self.stepMade = False
            self.stepT = allT[currTIdx]
            self.currentStep = self.steps[self.stepT]
            self.setPosition(self.currentStep[0])

    def prepareSteps(self):
        t = 1.0
        dIntensity = self.stepPSigma*150
        for pos in self.stepPositions:
            t += gauss(self.stepDt, 0.1)
            stepIntensity = gauss(150, dIntensity)
            self.steps[t] = (pos, stepIntensity)


