from field_types import FieldObject
import logging

class Geophone(FieldObject):
    """Ground vibration sensor""" 
    def __init__(self, entity, params):
        self.device = entity
        self.decayRate = params.get('decayRate', 10.0)
        self.device.environment.addFieldObject('Vibration', self)
        self.value = 0
        self.flagged = False


    def detectField(self, fieldValue):
        now = self.device.environment.time
        inTime = fieldValue.tArr
        self.value += fieldValue.intensity
        interp = -self.decayRate*(now-inTime)*self.value
        self.value += interp

    def getValue(self):
        return self.value

    def update(self, dt):
        # exponential decay
        decay = -self.decayRate*self.value*dt
        self.value += decay

    def getPosition(self):
        return self.device.physicsBody.getPosition()


