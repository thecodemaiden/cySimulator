from field_types import FieldObject

class Geophone(FieldObject):
    """Ground vibration sensor"""
    def __init__(self, entity, params):
        self.device = entity
        self.device.environment.addFieldObject('Vibration', self)
        self.value = 0

    def detectField(self, fieldValue):
        self.value = fieldValue.intensity

    def getValue(self):
        return self.value

    def update(self):
        pass #

    def getPosition(self):
        return self.device.physicsBody.getPosition()


