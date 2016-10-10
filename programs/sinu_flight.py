from device_task import DeviceTask
import logging
### Used quadcopter members:
###   getSensor
###   setPidTarget
###   getLogger (?)

### Needed from computational environment:
###     getTime

class SinuFlight(DeviceTask):
    """ Just keep the quadcopter hovering in place"""
    def setup(self):
        self.hasRadio = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio') # TODO: need gyro too for PID
        if radio is not None:
            #self.hasRadio = True
            self.radio = radio
        self.lastTime = self.environment.time

        return 10

    def loop(self):
        # assume we started in the right spot, y = 1.0m
        # adjust force to match 
        k = 0.1
        m = self.device.physicsBody.getMass().mass
        displacement = self.device.physicsBody.getPosition()[1]
        F = -k*displacement

        # we must apply this much force, + overcoming gravity
        F = F - self.environment.world.getGravity()[1]*m
        F = F/self.device.propellerThrustCoefficient

        self.device.setPidTarget([F, 0,0,0]);

        now = self.environment.time
        dt = now - self.lastTime
        logger = logging.getLogger(name='Quadsim.{}'.format(self.device.name))
        logger.info('Time: {:0.4f}\tPosition: {:0.4f}'.format(now, displacement))
        # send a message to radio a1b2c3d4e5
        if self.hasRadio:
            channel = self.radio.channel
             # all PID and radio stuff will move to programs
        
            if dt >= 0.5:
                self.radio.writePacket(0x12345678L, channel, "TEST")
                self.lastTime = self.environment.time
        #### log accel values  
        #v = self.sensors['acc'].getValue()
        #self.device.logger.info('{}.acc x: {}\ty: {}\tz: {}'.format(self.name, *v))
        ####
        return 50

taskClass = SinuFlight
