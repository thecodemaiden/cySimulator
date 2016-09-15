from device_task import DeviceTask

class BasicTx(DeviceTask):
    """Give the quads something to record"""
    def setup(self):
        self.hasRadio = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio') # TODO: need gyro too for PID
        if radio is not None:
            self.hasRadio = True
            self.radio = radio
        self.lastTime = self.environment.time
        return 0

    def loop(self):
        now = self.environment.time
        dt = now - self.lastTime
        if self.hasRadio:
            # send the packets to the quads
            if dt >= 0.5:
                self.radio.writePacket(now, 0xe7e7e7e7e7, self.radio.channel, 0xff)
                self.lastTime = dt
        return 10

taskClass = BasicTx