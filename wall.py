from ode import GeomBox
from my_object import PhysicalObject
class Wall(PhysicalObject):
    """A wall in the environment, which may contain rectangular holes"""
    def __init__(self, size, center_pos,  environment):
        super(Wall, self).__init__(environment)
        ls = self.environment.lengthScale
        self.dim = tuple(s*ls for s in size)
        self.centerPos = tuple(c*ls for c in center_pos)
        self.color = (0.5, 0.5, 0)
        self.makePhysicsBody()

    def __repr__(self):
        return (self.dim, self.centerPos)

    def makePhysicsBody(self):
        """ There is no actual physics body, just an immovable collision object """
        space = self.environment.space
        self.geom = GeomBox(space, self.dim)
        self.geom.setPosition(self.centerPos)

    def onVisualizationStart(self):
        p = self.environment.getGeomVizProperty(self.geom)
        p.SetColor(self.color)
        p.SetOpacity(0.16666)
        p.EdgeVisibilityOn()
    
    @classmethod
    def cutHoleInWall(cls, wall, hole_size, hole_center):
        ''' Returns up to four walls, which are pieces around the hole '''
        # TODO: make sure center lies in the wall (or some part of hole)
        if 0 in hole_size:
            return [wall]

        env = wall.environment



        hsx, hsy, hsz = hole_size
        hcx, hcy, hcz = hole_center

        wsx, wsy, wsz = [d/env.lengthScale for d in wall.dim]
        wcx, wcy, wcz = [d/env.lengthScale for d in wall.centerPos]

        pieces = []

        if hcz == 'z':
            # first cut along y axis at one x-side of the hole
            minX1 = wcx - wsx/2
            maxX1 = hcx - hsx/2
            xw1 = maxX1-minX1
            if (xw1 > 0) :
                #otherwise the piece has area 0 and we can ignore it
                w = Wall((xw1, wsy, wsz), ((maxX1+minX1)/2, wcy, wcz), env)
                pieces.append(w)
            # next cut, also along y axis, on other x-side of hole
            maxX2 = wcx + wsx/2
            minX2 = hcx + hsx/2
            xw2 = maxX2 - minX2
            if (xw2 > 0):
                w = Wall((xw2, wsy, wsz), ((maxX2+minX2)/2, wcy, wcz), env)
                pieces.append(w)

            #now two remaining pieces, on either y-side of the hole
            holeX1 = max(minX1, maxX1) # in case hole is specified bigger than wall....
            holeX2 = min(minX2, maxX2)
            xw3 = holeX2 - holeX1
            if (xw3 > 0):
                # can't see how it could be <= 0, but be safe I guess
                maxY1 = wcy + wsy/2
                minY1 = hcy + hsy/2
                yw1 = maxY1-minY1
                if yw1 > 0:
                    w = Wall((xw3, yw1, wsz), ((holeX2+holeX1)/2, (maxY1+minY1)/2, wcz), env)
                    pieces.append(w)
                minY2 = wcy - wsy/2
                maxY2 = hcy - hsy/2
                yw2 = maxY2 - minY2
                if yw2 > 0:
                    w = Wall((xw3, yw2, wsz), ((holeX2+holeX1)/2, (maxY2+minY2)/2, wcz), env)
                    pieces.append(w)

        return pieces




            
            

    @classmethod
    def makeRoom(cls, size, center, environment, wallThickness = 0.01):
        """ Convenience function for making a room and returning the list of walls """
        wallList = []
        sx,sy,sz = size
        cx, cy, cz = center
        t = wallThickness*environment.lengthScale

        # top (y+)
        w = cls((sx, t, sz), (cx, cy+sy/2+t/2, cz), environment)
        wallList.append(w)

        #bottom (y-)
        w = cls((sx, t, sz), (cx, cy-sy/2-t/2, cz), environment)
        wallList.append(w)

        #right (x+)
        w = cls((t, sy, sz), (cx+sx/2+t/2, cy, cz), environment)
        wallList.append(w)

        #left (x-)
        w = cls((t, sy, sz), (cx-sx/2-t/2, cy, cz), environment)
        wallList.append(w)

        #front (z+)
        w = cls((sx, sy, t), (cx, cy, cz+sz/2+t/2), environment)
        wallList.append(w)

        #back (z-)
        w = cls((sx, sy, t), (cx, cy, cz-sz/2-t/2), environment)
        wallList.append(w)

        return wallList
        

