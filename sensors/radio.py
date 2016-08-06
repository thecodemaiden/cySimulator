from object_types import FieldObject

class Radio(FieldObject):
    """A very simple radio implementation"""
    def __init__(self, onDevice, rx_sens=1e-10, tx_pow=0.1):
        self.device = onDevice
        self.rx_sensitivity = rx_sens # in W
        self.tx_power = tx_pow

        self.device.environment.addFieldObject('RF', self)

    def getRadiatedValue(self):
        return self.tx_power

    def getPosition(self):
        return self.device.physicsBody.getPosition()

    def getMaxRadiatedValue(self):
        return self.tx_power


