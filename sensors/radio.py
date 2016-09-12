from field_types import FieldObject
from random import randint
import numpy

class Radio(FieldObject):
    """A very simple radio implementation"""
    def __init__(self, entity, params):
        self.device = entity

        self.rx_sensitivity = float(params.get('rx_sens', 1e-10)) # in W
        self.tx_power = float(params.get('tx_pow', 0.01))
        self.channel = int(params['channel'])
        self.transFrequency = 2.4e9 + self.channel*1e6
        add = params.get('address')
        if add == None:
            # make up an address, hope it doesn't collide
            add = randint(0xb000000000L, 0xfefefefefeL)
        else:
            add = long(add, 16)
        self.address = add

        self.device.environment.addFieldObject('RF', self)
        self.lastRssi = 0
        self.emissionQueue = []

    def getRssi(self):
        return self.lastRssi

    def update(self, dt):
        # TODO: tx power up time?  rx delays?
        now = self.environment.time
        for val in self.emissionQueue[:]:
            if val[2] <= now:
                self.emissionQueue.remove(val)

    def detectField(self, fieldValue):
        """Register any readings, if necessary. fieldvalue is a FieldSphere """
        intensity = fieldValue.intensity
        if intensity >= self.rx_sensitivity:
            self.lastRssi = 10*numpy.log10(1000*intensity)
            #TODO: check address... ?!

    def getRadiatedValues(self):
        return (0, 0) # XXX: HAX!!self.tx_power

    def getPosition(self):
        return self.device.physicsBody.getPosition()





