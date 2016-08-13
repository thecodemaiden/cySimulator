import gc

class PhysicalObject(object):
    """Common methods for objects that are part of the physical simulation"""
    def __init__(self, environment):
        self.physicalEnvironment = environment

    def updatePhysics(self, dt):
        pass

    def drawExtras(self):
        pass

    def onVisualizationStart(self):
        pass

class ComputationalObject(object):
     """Common methods for objects that are part of the computational simulation"""
     def __init__(self, environment):
         pass
