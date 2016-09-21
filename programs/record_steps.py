import logging
from device_task import DeviceTask

class RecordSteps(DeviceTask):
    """Record vibration from geophone"""
    def setup(self):
        self.lastTime = 0
        deviceName = self.device.name
        self.logger = logging.getLogger(name='Quadsim.{}'.format(deviceName))
        return 0

    def loop(self):
        now = self.environment.time
        dt = now - self.lastTime
        geophone = self.device.getSensor('geophone')
        if geophone is not None:
            # send the packets to the quads
            if dt >= 0.1:
                self.logger.info('{}\t{}'.format(now, geophone.getValue()))
                self.lastTime = 0
        return 10

taskClass = RecordSteps