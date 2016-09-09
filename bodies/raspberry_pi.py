import ode
from object_types import Device

class Raspberry_Pi(Device):
    """A model of a Raspberry Pi computer - a very plain device spec"""

    def makePhysicsBody(self):
        physicsWorld = self.environment.world
        space = self.environment.space

        mainBody = ode.Body(physicsWorld)
        bodyMass = ode.Mass()
        totalMass = 0.1

        dims =  (0.2, 0.05, 0.1)

        bodyMass.setBoxTotal(totalMass, *dims)

        geom = ode.GeomBox(space, dims)
        geom.setCategoryBits(1)
        geom.setCollideBits(1)

        mainBody.setMass(bodyMass)
        geom.setBody(mainBody)

        self.geomList = [geom]
        self.physicsBody = mainBody

    def applyParameters(self, params):
        # no parameters needed... maybe in future clock speed, memory, etc
        pass

