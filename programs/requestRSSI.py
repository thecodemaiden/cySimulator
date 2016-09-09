from device_task import DeviceTask

class RequestRssi(DeviceTask):
    """Give the quads something to record"""
    def setup(self):
        self.hasRadio = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio') # TODO: need gyro too for PID
        if radio is not None:
            self.hasRadio = True
            self.radio = radio
        self.lastTime = self.environment.time
        self.quadAddresses = [0xe7e7e7e7e7L, 0xe7e7e7e7e6L, 0xe7e7e7e7e5L, 0xe7e7e7e7e4L, 0xe7e7e7e7e3L]
        return 0

    def loop(self):
        dt = self.environment.time - self.lastTime
        if self.hasRadio:
            # send the packets to the quads
            if dt >= 0.5:
                for add in self.quadAddresses:
                    self.radio.writePacket(add, self.radio.channel, 0xff)
                self.lastTime = dt
        return 10

taskClass = RequestRssi