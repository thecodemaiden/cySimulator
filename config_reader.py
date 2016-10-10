from ConfigParser import SafeConfigParser
from wall import Wall
from collections import defaultdict
import xml.etree.ElementTree as etree
import imp
from environment import PhysicalEnvironment, ComputeEnvironment, SimulationManager
import logging
from random import uniform, choice

# if there is a better way to access all bodies/sensors/etc, please do tell...
import bodies
import sensors
import programs
import field_types

class ConfigReader(object):
    """Reads the various option files"""
    def __init__(self, environment):
        self.environment = environment

    @classmethod
    def _mixedToFloats(cls, l):
        out = []
        for i in l:
            try:
                out.append(float(i))
            except ValueError:
                out.append(i)
        return out

    @classmethod
    def _extractListStr(cls, l):
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
                    wall = Wall(size, pos, self.environment, False)
                    color = w.findtext('color')
                    if color is not None:
                        color = [float(p) for p in self._extractListStr(color)]
                        wall.color = color
                    wallList[wallName] = wall

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

                obstacles = child.findall('obstacle')
                for o in obstacles:
                    wallName = o.attrib['name']
                    c = o.find('center')
                    pos = self._extractListStr(c.text)
                    pos = [float(p) for p in pos]
                    s = o.find('size')
                    size = self._extractListStr(s.text)
                    size = [float(p) for p in size]
                    wall = Wall(size, pos, self.environment, True)
                    color = o.findtext('color')
                    if color is not None:
                        color = [float(p) for p in self._extractListStr(color)]
                        wall.color = color
                    wallList[wallName] = wall


        holeWalls = []

        for key, dim in doorList.items():
            victimWall = key
            doorPos, doorSize = dim
            holeWalls += Wall.cutHoleInWall(wallList[victimWall], doorSize, doorPos)
            wallList.pop(victimWall)

        holeWalls += wallList.values()

        return holeWalls

    def loadDeviceTask(self, className):
        if className is None:
            return None
        try:
            taskClass = getattr(programs, className)
        except AttributeError:
            return None
        return taskClass

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

    @classmethod
    def readSimulationFile(cls, filename):
        bodyTree = etree.parse(filename)
        root = bodyTree.getroot()

        logFile = root.get('log')
        if logFile is not None:
            logger = logging.getLogger("Quadsim")
            # TODO - cleanup log handler at simulation end
            hndlr = logging.FileHandler(logFile, mode='a')
            hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
            logger.addHandler(hndlr)

        fs = root.get('sampleRate', '40')
        dt = 1.0/(float(fs))

        sim = SimulationManager(dt)
        cr = ConfigReader(sim) # TODO: these should all be class methods...?
        
        # create the fields
        fieldDescs = root.findall('field')
        for f in fieldDescs:
            name = f.attrib['name']
            className = f.attrib['class']
            try:
                fieldClass = getattr(field_types, className)
                params = f.findall('param')
                attrInfo = {}
                for p in params:
                    attrInfo.update(p.attrib)
                f = fieldClass(**attrInfo)
                sim.addField(name, f)
            except AttributeError:
                pass # TODO: log an error?

        # now read the layout file
        layout = root.find('layout')
        layoutFile = layout.attrib['file']

        startRegionsStr = layout.findall('startRegion')
        startRegions = []
        for r in startRegionsStr:
            t = r.text
            t=t.replace('(', '')
            t=t.replace(')', '')
            longStr = cls._extractListStr(t)
            left, bottom, back, right, top, front = [float(p) for p in longStr]
            startRegions.append(((left,bottom,back), (right, top, front)))

        walls = cr.readLayoutFile(layoutFile)
        for w in walls:
            sim.addObject(w)
            sim.addObstacle(w)

        # now add the devices
        slack = 0.1
        deviceTypes = root.findall('device')
        for dv in deviceTypes:
            bodyFile = dv.findtext('body')
            color = dv.findtext('color')
            namePrefix = dv.attrib.get('namePrefix', 'Device')
            devName = dv.attrib.get('name', None)
            sensorSpecs = dv.findall('sensor')
            taskName = dv.findtext('program')
            taskClass = cr.loadDeviceTask(taskName)
            sensorList = {}
            paramList = {}
            position = dv.findtext('position')
            if position is not None:
                position = [float(_) for _ in cr._extractListStr(position)]
            for s in sensorSpecs:
                className = s.attrib['class']
                try:
                    sensorClass = getattr(sensors, className)
                    name = s.attrib['name']
                    params = s.findall('param')
                    paramList[name] = {}
                    for p in params:
                        paramList[name].update(p.attrib) # TODO: params should be elements...
                    sensorList[name] = sensorClass
                except AttributeError:
                    pass
            nDevices = int(dv.findtext('count', 1))
            for i in range(nDevices):
                deviceBody = cr.readBodyFile(bodyFile)

                if devName is None:
                    devName = '{}_{:3d}'.format(namePrefix, i)
                deviceBody.name = devName
                for sn, s in sensorList.items():
                    deviceBody.addSensor(sn, s(deviceBody, paramList.get(sn, {})))
                sim.addObject(deviceBody)

                if position is None:
                    inRegion = choice(startRegions)

                    wallPadding = 0.15
                    x = uniform(inRegion[0][0]+wallPadding, inRegion[1][0]-wallPadding)
                    y = uniform(inRegion[0][1]+wallPadding, inRegion[1][1]-wallPadding)
                    z = uniform(inRegion[0][2]+wallPadding, inRegion[1][2]-wallPadding)
                else:
                    x,y,z = position
                deviceBody.setPosition((x,y,z))
                if taskClass is not None:
                    deviceBody.deviceTask = taskClass(deviceBody)
                if color is not None:
                    color = [float(x) for x in cr._extractListStr(color)]
                    deviceBody.color = color

        return sim




        







        
                    

            



