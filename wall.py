from ode import GeomBox
import numpy as np
from object_types import PhysicalObject

class Wall(PhysicalObject):
    """A wall in the environment, which may contain rectangular holes"""
    def __init__(self, size, center_pos,  environment):
        super(Wall, self).__init__(environment)
        ls = self.environment.lengthScale
        self.dim = tuple(s*ls for s in size)
        self.centerPos = tuple(c*ls for c in center_pos)
        self.faces = {}
        self.color = (0.5, 0.5, 0)
        self.makePhysicsBody()
        self.faces = []
        self.pts = []
        self.calculateFaces()


    def calculateFaces(self):
        top_left_front = (self.centerPos[0] - self.dim[0]/2, self.centerPos[1] + self.dim[1]/2, self.centerPos[2]-self.dim[2]/2)
        top_left_back = (self.centerPos[0] - self.dim[0]/2, self.centerPos[1] + self.dim[1]/2, self.centerPos[2]+self.dim[2]/2)
        top_right_front = (self.centerPos[0] + self.dim[0]/2, self.centerPos[1] + self.dim[1]/2, self.centerPos[2]-self.dim[2]/2)
        top_right_back = (self.centerPos[0] + self.dim[0]/2, self.centerPos[1] + self.dim[1]/2, self.centerPos[2]+self.dim[2]/2)

        bottom_left_front = (self.centerPos[0] - self.dim[0]/2, self.centerPos[1] - self.dim[1]/2, self.centerPos[2]-self.dim[2]/2)
        bottom_left_back = (self.centerPos[0] - self.dim[0]/2, self.centerPos[1] - self.dim[1]/2, self.centerPos[2]+self.dim[2]/2)
        bottom_right_front = (self.centerPos[0] + self.dim[0]/2, self.centerPos[1] - self.dim[1]/2, self.centerPos[2]-self.dim[2]/2)
        bottom_right_back = (self.centerPos[0] + self.dim[0]/2, self.centerPos[1] - self.dim[1]/2, self.centerPos[2]+self.dim[2]/2)

        #[x,y,z]

        self.pts = [ [ [], [] ], [ [], [] ] ]
        self.pts[0][0].insert(0, bottom_left_front)
        self.pts[0][0].insert(1, bottom_left_back)
        self.pts[0][1].insert(0, top_left_front)
        self.pts[0][1].insert(1, top_left_back)
        self.pts[1][0].insert(0, bottom_right_front)
        self.pts[1][0].insert(1, bottom_right_back)
        self.pts[1][1].insert(0, top_right_front)
        self.pts[1][1].insert(1, top_right_back)
        self.pts = np.array(self.pts)
        self.pts2 = np.square(self.pts)

        self.faces.append((0, top_left_back[0]))
        self.faces.append((0, top_right_back[0]))
        self.faces.append((1, top_left_back[1]))
        self.faces.append((1, bottom_left_back[1]))
        self.faces.append((2, top_left_back[2]))
        self.faces.append((2, top_left_front[2]))


        #self.faces['top'] = [top_left_front, top_right_front, top_right_back, top_left_back]
        #self.faces['bottom'] = [bottom_left_front, bottom_right_front, bottom_right_back, bottom_left_back]
        #self.faces['left'] = [top_left_front, top_left_back, bottom_left_back, bottom_left_front]
        #self.faces['right'] = [top_right_front, top_right_back, bottom_right_back, bottom_right_front]
        #self.faces['front'] = [top_left_front, top_right_front, bottom_right_front, bottom_left_front]
        #self.faces['back'] = [top_left_back, top_right_back, bottom_left_back, bottom_right_back]

    def __repr__(self):
        return str((self.dim, self.centerPos))

    def makePhysicsBody(self):
        """ There is no actual physics body, just an immovable collision object """
        space = self.environment.space
        self.geom = GeomBox(space, self.dim)
        self.geom.setPosition(self.centerPos)
        self.geom.setCategoryBits(2)
        self.geom.setCollideBits(1)

    def onVisualizationStart(self):
        g = self.environment.visualizer.getGraphics(self.geom)
        g.color = self.color
        g.opacity = 0.1
    
    @classmethod
    def cutHoleInWall(cls, wall, hole_size, hole_center):
        ''' Returns up to four walls, which are pieces around the hole '''
        # TODO: make sure center lies in the wall (or at least some part of hole)
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
        minFirstAxis1 =  scaledWallCenter[firstCutAxis] - scaledWallSize[firstCutAxis]/2 
        maxFirstAxis1 = hole_center[firstCutAxis] - hole_size[firstCutAxis] 
        firstAxisWidth1 = maxFirstAxis1 - minFirstAxis1 
        if (firstAxisWidth1 > 0) :
            #otherwise the piece has area <=0 and we can ignore it
            w = Wall((firstAxisWidth1, scaledWallSize[1], scaledWallSize[2]), 
                        ((maxFirstAxis1+minFirstAxis1)/2, scaledWallCenter[1], scaledWallCenter[2]), env)
            pieces.append(w)
        # next cut, also along y axis, on other x-side of hole
        maxFirstAxis2 = scaledWallCenter[firstCutAxis] + scaledWallSize[firstCutAxis]/2
        minFirstAxis2 = hole_center[firstCutAxis] + hole_size[firstCutAxis]/2
        firstAxisWidth2 = maxFirstAxis2 - minFirstAxis2
        if (firstAxisWidth2 > 0):
            w = Wall((firstAxisWidth2, scaledWallSize[1], scaledWallSize[2]), 
                        ((maxFirstAxis2+minFirstAxis2)/2, scaledWallCenter[1], scaledWallCenter[2]), env)
            pieces.append(w)

        #now two remaining pieces, on either y-side of the hole
        holeBegin = max(minFirstAxis1, maxFirstAxis1) 
        holeEnd = min(minFirstAxis2, maxFirstAxis2) 
        midPieceWidth = holeEnd - holeBegin 
        if (midPieceWidth > 0):
            # can't see how it could be <= 0, but be safe I guess
            maxSecondAxis1 = scaledWallCenter[secondCutAxis] + scaledWallSize[secondCutAxis]/2
            minSecondAxis1 = hole_center[secondCutAxis] + hole_size[secondCutAxis]/2
            secondAxisWidth1 = maxSecondAxis1 - minSecondAxis1
            if secondAxisWidth1 > 0:
                w = Wall((midPieceWidth, secondAxisWidth1, scaledWallSize[2]), 
                            ((holeBegin+holeEnd)/2, (maxSecondAxis1+minSecondAxis1)/2, scaledWallCenter[2]), env)
                pieces.append(w)
            minSecondAxis2 = scaledWallCenter[secondCutAxis] - scaledWallSize[secondCutAxis]/2
            maxSecondAxis2 = hole_center[secondCutAxis] - hole_size[secondCutAxis]/2
            secondAxisWidth2 = maxSecondAxis2 - minSecondAxis2
            if secondAxisWidth2 > 0:
                w = Wall((midPieceWidth, secondAxisWidth2, scaledWallSize[2]), 
                            ((holeBegin+holeEnd)/2, (maxSecondAxis2+minSecondAxis2)/2, scaledWallCenter[2]), env)
                pieces.append(w)

        return pieces

    @classmethod
    def makeRoom(cls, size, center, environment, wallThickness = 0.01):
        """ Convenience function for making a room and returning the list of walls """
        wallList = []
        sx,sy,sz = size
        cx, cy, cz = center
        t = wallThickness#*environment.lengthScale

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
        

