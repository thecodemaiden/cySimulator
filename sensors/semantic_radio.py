from field_types import FieldObject
import numpy
from random import randint

class RadioPacket:
    def __init__(self, address, channel, msg):
        self.address = address
        self.channel = channel
        self.message = msg

class SemanticRadio(FieldObject):
    """ A 'radio wave' representation where symbols are associated with wavefronts"""
    def __init__(self, entity, params):
        self.device = entity
        self.rx_sensitivity = float(params.get('rx_sens', 1e-10)) # in W
        self.tx_power = float(params.get('tx_pow', 0.01))
        self.inBuffer = [] # list of RadioPackets
        self.outBuffer = []
        self.lastRssi = 0
        self.channel = int(params['channel'])
        self.transFrequency = 2.4e9 + self.channel*1e6
        add = params.get('address')
        if add == None:
            # make up an address, hope it doesn't collide
            add = randint(0xb000000000L, 0xfefefefefeL)
        else:
            add = long(add, 16)
        self.address = add
        self.device.environment.addFieldObject('RF_Semantic', self)

    def detectField(self, fieldValue):
        """Register any readings, if necessary. fieldvalue is a FieldSphere """
        intensity = fieldValue.intensity
        packet = fieldValue.data
        if intensity >= self.rx_sensitivity:
            # TODO: multiple addresses + channels possible!
            if packet.address == self.address and packet.channel == self.channel:
                self.inBuffer.append(packet.message) # TODO: timestamp? 
                self.lastRssi = 10*numpy.log10(1000*intensity)


    def writePacket(self, address, channel, message):
        pack = RadioPacket(address, channel, message)
        self.outBuffer.append(((self.transFrequency, self.tx_power), pack))

    def isAvailable(self):
        return len(self.inBuffer) > 0

    def readPacket(self, nBytes=-1):
        #if nBytes < 0 or nBytes > len(self.inBuffer):
        #    nBytes = len(self.inBuffer)
        #output = self.inBuffer[-nBytes:]
        #self.inBuffer = self.inBuffer[:nBytes]
        return self.inBuffer.pop()

    def getRadiatedValues(self):
        if len(self.outBuffer) > 0:
            info = self.outBuffer.pop(0)
            return [info]
        return [(None, None)]


    def getPendingEmission(self):
        if len(self.emissionQueue) == 0:
            return None
        return self.emissionQueue[0]

    def getRssi(self):
        return self.lastRssi

    def update(self, dt):
        pass
        # TODO: tx power up time?  rx delays?
        #now = self.environment.time
        #for val in self.emissionQueue[:]:
        #    if val[2] <= now:
        #        self.emissionQueue.remove(val)

    def getPosition(self):
        return self.device.physicsBody.getPosition()