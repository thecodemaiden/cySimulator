## TODO: should we return the time taken, for scheduling purposes

## TODO: make it easier to get physical and computational env. from sim manager

class DeviceTask(object):
    """Encapsulates the initial and recurring aspects of a task"""
    def __init__(self, device):
        self.device = device
        self.manager = device.environment.manager
    
    def setup(self):
        pass

    def loop(self):
        pass


