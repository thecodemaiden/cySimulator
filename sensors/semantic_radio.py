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
        self.transFrequency = float(params.get('frequency', 2.4e9))
        self.rx_sensitivity = float(params.get('rx_sens', 2.5e-13)) # in W, for nrf51
        self.tx_power = float(params.get('tx_pow', 0.0001)) # nrf51
        self.inBuffer = [] # list of RadioPackets
        self.outBuffer = []
        self.lastRssi = 0
        self.channel = int(params['channel'])
        self.transFrequency += self.channel*1e6
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
                newRssi = 10*numpy.log10(1000*intensity)
                self.lastRssi = newRssi


    def writePacket(self, t, address, channel, message):
        pack = RadioPacket(address, channel, message)
        self.outBuffer.append(((self.transFrequency, self.tx_power, t), pack))

    def isAvailable(self):
        return len(self.inBuffer) > 0

    def readPacket(self, nBytes=-1):
        return self.inBuffer.pop()

    def getRadiatedValues(self):
        if len(self.outBuffer) > 0:
            outPackets = [p for p in self.outBuffer if self.device.environment.time >= p[0][2]]
            self.outBuffer = [p for p in self.outBuffer if p not in outPackets]
            return outPackets
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