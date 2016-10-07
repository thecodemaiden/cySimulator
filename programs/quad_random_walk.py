from device_task import DeviceTask
from random import randint, uniform

### Used quadcopter members:
###   getSensor
###   setPidTarget
###   getLogger (?)

### Needed from computational environment:
###     getTime
class QuadRandomWalk(DeviceTask):
    """ Random walk, 10Hz update; read accel at 1Hz"""
    def setup(self):
        self.hasRadio = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio')
        self.accel = self.device.getSensor('acc')
        if radio is not None:
            self.hasRadio = True
            self.radio = radio
        self.device.setPidTarget([-1,0,0,0])
        self.doBroadcast = True
        self.lastMoveTime = self.environment.time
        self.lastAccelTime = self.environment.time
        self.lastBroadcastTime = self.environment.time

        return 10

    def loop(self):
        now = self.environment.time
        # random walk
        if now - self.lastMoveTime >= 0.1:
            self.lastMoveTime = now
            p = uniform(-.08,.08)
            r = uniform(-.08,.08)
            self.device.setPidTarget([-1, p,r,0])
        if now - self.lastAccelTime >= 1.0:
            self.lastAccelTime = now
            accelVal = self.accel.getValue()
        if self.doBroadcast and self.hasRadio and now - self.lastBroadcastTime >= 1.0:
            self.lastBroadcastTime = now
            self.radio.writePacket(now, 0x1234567890L, self.radio.channel, "Beep")
        return 50

taskClass = QuadRandomWalk
