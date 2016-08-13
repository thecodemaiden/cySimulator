import gc

class PhysicalObject(object):
    """Common methods for objects that are part of the physical simulation"""
    def __init__(self, environment):
        self.environment = environment

    def update(self, dt):
        pass

    def drawExtras(self):
        pass

    def onVisualizationStart(self):
        pass