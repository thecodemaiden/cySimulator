from device_task import DeviceTask

class SendRssi(DeviceTask):
    """Just sit tight and record RSSI"""
    def setup(self):
        self.hasRadio = False # we need to make sure there is a radio before we can run the loop
        radio = self.device.getSensor('radio') # TODO: need gyro too for PID
        if radio is not None:
            self.hasRadio = True
            self.radio = radio
        self.lastTime = self.environment.time

        return 0

    def loop(self):
        dt = self.environment.time - self.lastTime
        # send a message to radio a1b2c3d4e5
        if self.hasRadio:
            # TODO: 'send' RSSI to RPi
            channel = self.radio.channel
            if dt >= 0.5:
                self.device.logger.info('RSSI: {}'.format(self.radio.lastRssi))
                self.lastTime = dt
        return 10

taskClass = SendRssi