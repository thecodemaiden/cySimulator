from field_types import FieldObject
from random import randint
import numpy

class Radio(FieldObject):
    """A very simple radio implementation"""
    def __init__(self, entity, params):
        self.device = entity

        self.transFrequency = float(params.get('frequency', 2.4e9))
        self.rx_sensitivity = float(params.get('rx_sens', 1e-10)) # in W
        self.tx_power = float(params.get('tx_pow', 0.01))
        self.channel = int(params['channel'])
        self.transFrequency += self.channel*1e6
        add = params.get('address')
        if add == None:
            # make up an address, hope it doesn't collide
            add = randint(0xb000000000L, 0xfefefefefeL)
        else:
            add = long(add, 16)
        self.address = add
        self.environment = self.device.environment
        self.device.environment.addFieldObject('RF', self)
        self.lastRssi = 0
        self.emissionQueue = []

    def getRssi(self):
        return self.lastRssi

    def update(self, dt):
        # TODO: tx power up time?  rx delays?
        pass

    def writePacket(self, t, address, channel, message):
        # ignore message
        toEmit = (self.transFrequency, self.tx_power, t)
        self.emissionQueue.append(toEmit)


    def detectField(self, fieldValue):
        """Register any readnigs, if necessary. fieldvalue is a FieldSphere """
        intensity = fieldValue.intensity
        if intensity >= self.rx_sensitivity:
            self.lastRssi = 10*numpy.log10(1000*intensity)
            #TODO: check address... ?!

    def getRadiatedValues(self):
        outVals = []
        now = self.environment.time
        for e in self.emissionQueue[:]:
            if e[2] <= now:
                outVals.append(e)
                self.emissionQueue.remove(e)
        return outVals

    def getPosition(self):
        return self.device.physicsBody.getPosition()





