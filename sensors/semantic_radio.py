from field_types import FieldObject

class RadioPacket:
    def __init__(self, address, channel, msg):
        self.address = address
        self.channel = channel
        self.message = msg

class SemanticRadio(FieldObject):
    """ A 'radio wave' representation where symbols are associated with wavefronts"""
    def __init__(self, onDevice, address, channel, rx_sens = 1e-10, tx_pow = 0.01):
        self.device = onDevice
        self.rx_sensitivity = rx_sens # in W
        self.tx_power = tx_pow
        self.inBuffer = [] # list of RadioPackets
        self.outBuffer = []
        self.channel = channel
        self.address = address

        self.device.environment.addFieldObject('RF_Semantic', self)

    def detectField(self, fieldValue):
        """Register any readings, if necessary. fieldvalue is a FieldSphere """
        intensity = fieldValue.intensity
        packet = fieldValue.data
        if intensity >= self.rx_sensitivity:
            # TODO: multiple addresses + channels possible!
            if packet.address == self.address and packet.channel == self.channel:
                self.inBuffer.append(packet.message) # TODO: timestamp? 

    def writePacket(self, address, channel, message):
        pack = RadioPacket(address, channel, message)
        self.outBuffer.append((self.tx_power, pack))

    def isAvailable(self):
        return len(self.inBuffer) > 0

    def readPacket(self, nBytes=-1):
        if nBytes < 0 or nBytes > len(self.inBuffer):
            nBytes = len(self.inBuffer)
        output = self.inBuffer[-nBytes:]
        self.inBuffer = self.inBuffer[:nBytes]
        return output

    def getRadiatedValue(self):
        if len(self.outBuffer) > 0:
            info = self.outBuffer.pop(0)
            return info
        return None

    def getPosition(self):
        return self.device.physicsBody.getPosition()

    def getMaxRadiatedValue(self):
        return self.tx_power



