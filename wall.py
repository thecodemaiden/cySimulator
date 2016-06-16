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
        

