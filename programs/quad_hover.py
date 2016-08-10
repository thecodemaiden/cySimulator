from device_task import DeviceTask


### Used quadcopter members:
###   getSensor
###   setPidTarget
###   getLogger (?)

### Needed from computational environment:
###     getTime

class QuadHover(DeviceTask):
    """ Just keep the quadcopter hovering in place"""
    def setup(self):
        self.canRun = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio') # TODO: need gyro too
        if radio is not None:
            self.canRun = True
            self.radio = radio

    def loop(self):
        # send a message to radio a1b2c3d4e5
        
        channel = self.radio.channel
        # all PID and radio stuff will move to programs
        if self.time % 2.5 < dt:
            r.writePacket(RADIO_ADDR, RADIO_CHAN, "TEST")
        ####
        '''
                #### MOVE TO PROGRAM
        v = self.sensors['acc'].getValue()
        self.logger.info('{}.acc x: {}\ty: {}\tz: {}'.format(self.name, *v))
        ####
        '''

taskClass = QuadHover
