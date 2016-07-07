from ConfigParser import SafeConfigParser
from wall import Wall
from collections import defaultdict
import xml.etree.ElementTree as etree

# if there is a better way to access all bodies, please do tell...
import bodies

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

        for key, dim in doorList.items():
            victimWall = key
            doorPos, doorSize = dim
            holeWalls += Wall.cutHoleInWall(wallList[victimWall], doorSize, doorPos)
            wallList.pop(victimWall)

        holeWalls += wallList.values()

        return holeWalls

    def readBodyFile(self, filename):
        bodyTree = etree.parse(filename)
        root = bodyTree.getroot()

        className = root.attrib['class']
        try:
            bodyClass = getattr(bodies, className)
        except AttributeError:
            return None # no such body
        params = {}
        params['environment'] = self.environment
        xmlParams = root.findall('param')
        for p in xmlParams:
            params[p.attrib['name']] = p.attrib['value']
            # todo: add type to xml and cast here
        newBody = bodyClass(params)
        return newBody




        
                    

            



