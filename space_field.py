import ode
import gc

class OdeFieldSphere(object):
    startR = 0.0
    def __init__(self, center, totalPower, space, data=None):
        self.totalPower = totalPower
        self.data = data
        self.geom = ode.GeomSphere(space, self.startR)
        self.geom.setPosition(center)
        self.geom.setCategoryBits = 8
        self.geom.setCollideBits = 3
        self.intensity = None
        self.lastRadius = self.startR

class OdeFieldTestObject(object):
    def __init__(self):
        pass

    def getPosition(self):
        return (0,0,0)

    def getRadiatedValue(self):
        return 0.5

class OdeField(object):
    def __init__(self,propSpeed, physicalSpace):
        self.objects = {}
        self.speed = float(propSpeed)
        self.fieldSpace =  ode.HashSpace() # ode.QuadTreeSpace((0,0,0), (11.0, 5.0, 20.0), 3)
        self.physicalSpace = physicalSpace
        self.minI = 10e-10
        self.collisionRemoved = set()

    def addObject(self, o):
        if o not in self.objects:
            self.objects[o] = []

    def updateSphereValue(self, s, dt):
        # we need to expand it, and if power density is too low, remove it
        if s.geom.getSpace() is None:
            return None
        if s.intensity is not None and s.intensity < self.minI:
            return None
        r = s.geom.getRadius()
        s.lastRadius = r
        r += dt*self.speed
        s.geom.setRadius(r)
        s.intensity = s.totalPower/(r**2)
        return s

    def update(self, dt):
        oList = self.objects.items()
        for o, sphereList in oList:
            gc.disable()
            toRemove = []
            newList = []
            # add the newest sphere
            newSphere = OdeFieldSphere(o.getPosition(), o.getRadiatedValue(), self.fieldSpace)
            newList.append(newSphere)
            for s in sphereList:
                # see which are to be removed
                updatedS = self.updateSphereValue(s, dt)
                if updatedS is None:
                    toRemove.append(s)
                else:
                    newList.append(s)
            self.objects[o] = newList
            for s in toRemove:
                self.fieldSpace.remove(s.geom)
            gc.enable()
        # now see what geoms collide 
        ode.collide2(self.fieldSpace, self.physicalSpace, None, self.nearCallback)
        for g in self.collisionRemoved:
            self.fieldSpace.remove(g)
        self.collisionRemoved.clear()

    def nearCallback(self, args, geom1, geom2):
        contacts = ode.collide(geom1, geom2)
        c = contacts[0]
        pos, normal, depth, g1, g2 = c.getContactGeomParams()
        if g1.getCategoryBits() == 2:
            self.collisionRemoved.add(g2)
        elif g2.getCategoryBits() == 2:
            self.collisionRemoved.add(g1)
        #print 'Contact detected at {:2.2f},{:2.2f},{:2.2f}:\n\tdepth:{:2.2f}\t normal:{:2.2f},{:2.2f},{:2.2f}'.format(
        #    pos[0], pos[1], pos[2], depth, *normal)
        # don't  make contact joints
        pass





