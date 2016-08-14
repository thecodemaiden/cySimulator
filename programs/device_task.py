## TODO: should we return the time taken, for scheduling purposes?
class DeviceTask(object):
    """Encapsulates the initial and recurring aspects of a task"""
    def __init__(self, device):
        self.device = device
        self.environment = device.environment
        self.__runner = self.__runnerGen()
    
    def __runnerGen(self):
        yield self.setup()
        while True:
            yield self.loop()
    
    def tick(self, dt):
        return self.__runner.next()
        

    def setup(self):
        return 0 # how long it took?

    def loop(self):
        return 0 # how long it took?


