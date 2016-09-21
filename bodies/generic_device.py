import ode
from object_types import Device

class GenericDevice(Device):
    """A box-shaped device"""

    def makePhysicsBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space

        mainBody = ode.Body(physicsWorld)
        bodyMass = ode.Mass()
        totalMass = 0.075


        bodyMass.setBoxTotal(totalMass, *self.dims)

        geom = ode.GeomBox(space, self.dims)
        geom.setCategoryBits(1)
        geom.setCollideBits(1)

        mainBody.setMass(bodyMass)
        geom.setBody(mainBody)

        self.geomList = [geom]
        self.physicsBody = mainBody

    def applyParameters(self, params):
        # no parameters needed... maybe in future clock speed, memory, etc
        dims = params['size']
        dims = [float(c) for c in dims.split(',')]
        self.dims = dims

    def updatePhysics(self, dt):
        for s in self.sensors.values():
            s.update(dt)

