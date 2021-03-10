import ode
from object_types import Device
from field_types import FieldObject
from random import gauss
from bisect import bisect_left
from sensors import Geophone

class SimStepper(Device, FieldObject):
    """An object with no body that generates fake footstep vibrations"""
    def makePhysicsBody(self):
        physicsWorld = self.environment.world

        mainBody = ode.Body(physicsWorld)
        mainBody.setKinematic()
       
        self.physicsBody = mainBody
        self.environment.addFieldObject('Vibration', self)


    def getRadiatedValues(self):
        if not self.stepMade:
            if self.lastT >= self.stepT:
                self.stepMade = True
                return [(360, self.currentStep[1], self.stepT)]
        return [(None, None, None)]

    def applyParameters(self, params):
        # time, step position, relative intensity
        posStr = params['stepPositions']
        posList = posStr.split(';')
        self.stepPositions = []
        for p in posList:
            p = [float(i) for i in p.split(',')]
            p[0] = p[0] +0.2;
            self.stepPositions.append(p)
        stepT = params.get('stepTimes')
        if stepT is not None:
            self.stepTimes = [float(x) for x in stepT.split(';')]
        else:
            self.stepTimes = self.generateStepTimes(len(self.stepPositions))

        self.stepDt = float(params.get('stepDt', 1.0))
        self.stepTSigma = float(params.get('stepTSigma', 0.1))
        self.stepPSigma = float(params.get('stepPSigma', 0.1))
    
        self.stepMade  = False
        self.lastT = 0
        self.steps = {}
        self.prepareSteps()
        self.stepT = self.stepTimes[0]
        self.currentStep = self.steps[self.stepT]

    def generateStepTimes(self, n):
        t = 0.4
        arr = []
        for i in range(n):
            t += abs(gauss(self.stepDt, self.stepTSigma))
            arr.append(t)

        return arr

    def updatePhysics(self, dt):
        self.lastT = self.environment.time
        currTIdx = bisect_left(self.stepTimes, self.lastT)
        # the value at currTIdx >= now
        if currTIdx >= len(self.stepTimes):
            return
        if self.stepMade and self.stepTimes[currTIdx] != self.stepT:
            self.stepMade = False
            self.stepT = self.stepTimes[currTIdx]
            self.currentStep = self.steps[self.stepT]
        self.setPosition(self.currentStep[0])

            

    def prepareSteps(self):
        n = len(self.stepPositions)
        intensity = 20
        dIntensity = self.stepPSigma*intensity
        for i in range(n):
            stepIntensity = gauss(intensity, dIntensity)
            self.steps[self.stepTimes[i]] = (self.stepPositions[i], stepIntensity)


