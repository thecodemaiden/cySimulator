from device_task import DeviceTask
from random import randint

### Used quadcopter members:
###   getSensor
###   setPidTarget
###   getLogger (?)

### Needed from computational environment:
###     getTime

class QuadHover(DeviceTask):
    """ Just keep the quadcopter hovering in place"""
    def setup(self):
        self.hasRadio = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio') # TODO: need gyro too for PID
        if radio is not None:
            self.hasRadio = True
            self.radio = radio
        coinFlip = randint(0,1)
        self.stayStill = coinFlip == 0
        self.lastTime = self.environment.time
        return 10

    def loop(self):
        if self.stayStill:
            self.device.setPidTarget([0,0,0])
        else:
            self.device.setPidTarget([0.05, 0, 0])
        dt = self.environment.time - self.lastTime
        # send a message to radio a1b2c3d4e5
        if self.hasRadio:
            channel = self.radio.channel
             # all PID and radio stuff will move to programs
        
            if dt >= 2.5:
                self.radio.writePacket(0x12345678L, channel, "TEST")
        self.lastTime = self.environment.time
        #### log accel values  
        #v = self.sensors['acc'].getValue()
        #self.device.logger.info('{}.acc x: {}\ty: {}\tz: {}'.format(self.name, *v))
        ####
        return 50

taskClass = QuadHover
