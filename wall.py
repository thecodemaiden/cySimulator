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
        #p.SetOpacity(0.16666)
        #p.SetRepresentationToWireframe()
        p.EdgeVisibilityOn()
    
    @classmethod
    def cutHoleInWall(cls, wall, hole_size, hole_center):
        ''' Returns up to four walls, which are pieces around the hole '''
        # TODO: make sure center lies in the wall (or some part of hole)
        if 0 in hole_size:
            return [wall]

        env = wall.environment


        scaledWallSize = [d/env.lengthScale for d in wall.dim]
        scaledWallCenter = [d/env.lengthScale for d in wall.centerPos]

        pieces = []
        if hole_size[2] == 'z':
            firstCutAxis = 0
            secondCutAxis = 1
            thicknessAxis = 2

        # first cut along y axis at one x-side of the hole
        minFirstAxis1 =  scaledWallCenter[firstCutAxis] - scaledWallSize[firstCutAxis]/2 #wcx - wsx/2
        maxFirstAxis1 = hole_center[firstCutAxis] - hole_size[firstCutAxis] #hcx - hsx/2
        firstAxisWidth1 = maxFirstAxis1 - minFirstAxis1 # maxX1-minX1
        if (firstAxisWidth1 > 0) :
            #otherwise the piece has area <=0 and we can ignore it
            #  Wall((xw1, wsy, wsz), ((maxX1+minX1)/2, wcy, wcz), env)
            w = Wall((firstAxisWidth1, scaledWallSize[1], scaledWallSize[2]), 
                        ((maxFirstAxis1+minFirstAxis1)/2, scaledWallCenter[1], scaledWallCenter[2]), env)
            pieces.append(w)
        # next cut, also along y axis, on other x-side of hole
        maxFirstAxis2 = scaledWallCenter[firstCutAxis] + scaledWallCenter[firstCutAxis]/2#wcx + wsx/2
        minFirstAxis2 = hole_center[firstCutAxis] + hole_size[firstCutAxis]/2#hcx + hsx/2
        firstAxisWidth2 = maxFirstAxis2 - minFirstAxis2 #maxX2 - minX2
        if (firstAxisWidth2 > 0):
            # Wall((xw2, wsy, wsz), ((maxX2+minX2)/2, wcy, wcz), env)
            w = Wall((firstAxisWidth2, scaledWallSize[1], scaledWallSize[2]), 
                        ((maxFirstAxis2+minFirstAxis2)/2, scaledWallCenter[1], scaledWallCenter[2]), env)
            pieces.append(w)

        #now two remaining pieces, on either y-side of the hole
        holeBegin = max(minFirstAxis1, maxFirstAxis1) #max(minX1, maxX1) in case hole is specified bigger than wall....
        holeEnd = min(minFirstAxis2, maxFirstAxis2) # min(minX2, maxX2)
        midPieceWidth = holeEnd - holeBegin #holeX2 - holeX1
        if (midPieceWidth > 0):
            # can't see how it could be <= 0, but be safe I guess
            maxSecondAxis1 = scaledWallCenter[secondCutAxis] + scaledWallSize[secondCutAxis]/2
            minSecondAxis1 = hole_center[secondCutAxis] + hole_size[secondCutAxis]/2
            secondAxisWidth1 = maxSecondAxis1 - minSecondAxis1
            if secondAxisWidth1 > 0:
                # w = Wall((xw3, yw1, wsz), ((holeX2+holeX1)/2, (maxY1+minY1)/2, wcz), env)
                w = Wall((midPieceWidth, secondAxisWidth1, scaledWallSize[2]), 
                            ((holeBegin+holeEnd)/2, (maxSecondAxis1+minSecondAxis1)/2, scaledWallCenter[2]), env)
                #pieces.append(w)
            minSecondAxis2 = scaledWallCenter[secondCutAxis] - scaledWallSize[secondCutAxis]/2
            maxSecondAxis2 = hole_center[secondCutAxis] - hole_size[secondCutAxis]/2
            secondAxisWidth2 = maxSecondAxis2 - minSecondAxis2
            if secondAxisWidth2 > 0:
                w = Wall((midPieceWidth, secondAxisWidth2, scaledWallSize[2]), 
                            ((holeBegin+holeEnd)/2, (maxSecondAxis2+minSecondAxis2)/2, scaledWallCenter[2]), env)
                #pieces.append(w)



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
        

