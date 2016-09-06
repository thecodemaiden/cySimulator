from field_types import FieldObject
from random import randint

class Radio(FieldObject):
    """A very simple radio implementation"""
    def __init__(self, entity, params):
        self.device = entity

        self.rx_sensitivity = float(params.get('rx_sens', 1e-10)) # in W
        self.tx_power = float(params.get('tx_pow', 0.01))
        self.channel = int(params['channel'])
        if params.get('address') == None:
            # make up an address, hope it doesn't collide
            add = randint(0xa0a0a0a0a0L, 0xfefefefefeL)
        else:
            add = long(params['address'])
        self.address = add

        self.device.environment.addFieldObject('RF', self)
        self.lastRssi = 0

    def getRssi(self):
        return self.lastRssi

    def update(self, dt):
        # TODO: tx power up time? rx delays?
        pass

    def detectField(self, fieldValue):
        """Register any readings, if necessary. fieldvalue is a FieldSphere """
        intensity = fieldValue.intensity
        if intensity >= self.rx_sensitivity:
            # TODO: multiple addresses + channels possible!
            if packet.address == self.address and packet.channel == self.channel:
                pass # we got it...

    def writePacket(self, address, channel, txTime):
        pass

    def readPacket(self, nBytes=-1):
        if nBytes < 0 or nBytes > len(self.inBuffer):
            nBytes = len(self.inBuffer)
        output = self.inBuffer[-nBytes:]
        self.inBuffer = self.inBuffer[:nBytes]
        return output

    def getRadiatedValue(self):
        return 0

    def getPosition(self):
        return self.device.physicsBody.getPosition()





