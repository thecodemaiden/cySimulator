from ConfigParser import SafeConfigParser
from wall import Wall
from collections import defaultdict
import xml.etree.ElementTree as etree

class ConfigReader(object):
    """Reads the various option files"""
    def __init__(self, environment):
        self.environment = environment

    def _mixedToFloats(self, l):
        out = []
        for i in l:
            try:
                out.append(float(i))
            except ValueError:
                out.append(i)
        return out

    def _extractListStr(self, l):
        l = l.replace(' ', '')

        return l.split(',')


    def readLayoutFile(self, filename):
        layoutTree = etree.parse(filename)
        root = layoutTree.getroot()
        wallList = {}
        doorList = defaultdict(dict)
        
        for child in root:
            if child.tag == 'room':
                # parse the walls
                walls = child.findall('wall')
                for w in walls:
                    wallName = w.attrib['name']
                    c = w.find('center')
                    pos = self._extractListStr(c.text)
                    pos = [float(p) for p in pos]
                    s = w.find('size')
                    size = self._extractListStr(s.text)
                    size = [float(p) for p in size]
                    wallList[wallName] = Wall(size, pos, self.environment)

                doors = child.findall('door')
                for d in doors:
                    wallName = d.attrib['wall']
                    c = d.find('center')
                    pos = self._extractListStr(c.text)
                    pos = self._mixedToFloats(pos)
                    s = d.find('size')
                    size = self._extractListStr(s.text)
                    size = self._mixedToFloats(size)
                    doorList[wallName] = (pos, size)

        holeWalls = []

        #for key, dim in doorList.items():
        #    victimWall = key
        #    doorPos, doorSize = dim
        #    holeWalls += Wall.cutHoleInWall(wallList[victimWall], doorSize, doorPos)
        #    wallList.pop(victimWall)

        holeWalls += wallList.values()

        return holeWalls

        
                    

            



