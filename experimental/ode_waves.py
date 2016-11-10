import ode

class Field(object):
     def __init__(self, propSpeed, minIntensity=1e-20):
         self.speed = propSpeed
         self.minI = minIntensity
         self.space = ode.QuadTreeSpace((0,0,0), (5,5,5), 4)

class FieldShell(object):
    def __init__(self, center, speed, frequency, totalPower, startTime, endTime, space):
        self.center = center
        self.speed = speed
        self.frequency=frequency
        self.totalPower = totalPower
        self.startT = startTime
        self.endT = endTime

        self.fieldSpace = space

        self.geom1 = None
        self.geom2 = None

        self.r1 = self.r2 = 0

    def update(self, t):
        self.r1 = self.speed*(t - self.startT)
        self.r2 = self.speed*(t - self.endT)

        if self.geom1 is not None:
            self.geom1.setRadius(self.r1)
        else:
            self.geom1 = ode.GeomSphere(self.fieldSpace, self.r1)
            self.geom1.setPosition(self.center)
            self.geom1.parent = self
            
        if self.geom2 is not None:
            self.geom2.setRadius(self.r2)
        else:
            self.geom2 = ode.GeomSphere(self.fieldSpace, self.r2)
            self.geom2.setPosition(self.center)
            self.geom2.parent = self
             


if __name__ == '__main__':
    #space = ode.QuadTreeSpace((0,0,0), (5,5,5), 4)
    import visual as v
    space = ode.HashSpace()
    t = 3
    wave1 = FieldShell((0,0,0), 1, 20, 0.5, 0.25, 0.5, space)
    wave2 = FieldShell((0,0,5), 1, 20, 0.5, 1.5, 1.9, space)

    wave1.update(t)
    wave2.update(t)

    scene = v.display(title='Shell sim', width=640, height=480, background=(0.8,0.8,0.8))

    sphere11 = v.sphere(pos=wave1.center, color=(1,0,0), opacity=0.3, display=scene)
    sphere12 = v.sphere(pos=wave1.center, color=(0.5,0,1), opacity=0.7, display=scene)
    sphere21 = v.sphere(pos=wave2.center, color=(0,1,0), opacity=0.3, display=scene)
    sphere22 = v.sphere(pos=wave2.center, color =(0,0.5,1), opacity=0.7, display=scene)


    def updateSpheres():
        sphere11.radius = wave1.r1
        sphere12.radius = wave1.r2
        sphere21.radius = wave2.r1
        sphere22.radius = wave2.r2

    def near_callback(args, geom1, geom2):
        # Check if the objects do collide
        if geom1.parent != geom2.parent:
            contacts = ode.collide(geom1, geom2)
            print('{} contacts created'.format(len(contacts)))
           

    updateSpheres()
    for i in range(2000):
        v.rate(60)
        t += 0.001
        wave1.update(t)
        wave2.update(t)
        space.collide(None, near_callback)
        updateSpheres()
    

