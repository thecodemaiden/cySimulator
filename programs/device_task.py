## TODO: should we return the time taken, for scheduling purposes
class DeviceTask(object):
    """Encapsulates the initial and recurring aspects of a task"""
    def __init__(self, device):
        self.device = device
        self.environment = device.environment
    
    def setup(self):
        pass

    def loop(self):
        pass


