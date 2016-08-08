import numpy as np

class Accelerometer(object):
    ''' Returns the body-frame accelerometer reading, including (default) or excluding gravity '''
    def __init__(self, entity, params):
        self.entity = entity
        self.lastVel = self.entity.physicsBody.getLinearVel()
        self.acc = np.full((1,3), 0.0)
        self.accGrav =  np.full((1,3), 0.0)

    def update(self, dt):
        body = self.entity.physicsBody
        world = self.entity.environment.world
        fs = self.entity.environment.forceScale

        vel = body.getLinearVel() # world frame 

        dv = np.array([vel[i] - self.lastVel[i] for i in range(3)])
        worldFrameAcc = (dv/dt).reshape(3,1)
       
        worldGrav = np.array(world.getGravity()).reshape(3,1) # need a column vector

        bodyRot = body.getRotation()
        bodyRot = np.array(bodyRot).reshape(3,3)
        bodyRotT = bodyRot.transpose()
        gravRotated = np.dot(bodyRotT, worldGrav)

        bodyFrameAcc = np.dot(bodyRotT, worldFrameAcc)
        self.acc = bodyFrameAcc/fs
        self.accGrav = (bodyFrameAcc + gravRotated)/fs
        self.lastVel = vel

    def getValue(self, withGravity=False):
        if not withGravity:
            v = self.acc
        else:
            v = self.accGrav
        return v.flatten()