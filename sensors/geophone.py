from field_types import FieldObject
import logging

class Geophone(FieldObject):
    """Ground vibration sensor"""
    def __init__(self, entity, params):
        self.device = entity
        deviceName = self.device.name
        self.decayRate = params.get('decayRate', 14.0)
        self.device.environment.addFieldObject('Vibration', self)
        self.value = 0

    def detectField(self, fieldValue):
        self.value += fieldValue.intensity

    def getValue(self):
        return self.value

    def update(self, dt):
        # exponential decay
        decay = -self.decayRate*self.value*dt
        self.value += decay

    def getPosition(self):
        return self.device.physicsBody.getPosition()


