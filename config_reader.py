from ConfigParser import SafeConfigParser
from wall import Wall
from collections import defaultdict
import xml.etree.ElementTree as etree

from environment import PhysicalEnvironment, ComputeEnvironment, SimulationManager
import logging
from random import uniform

# if there is a better way to access all bodies/sensors/etc, please do tell...
import bodies
import sensors
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

    @classmethod
    def readSimulationFile(cls, filename):
        bodyTree = etree.parse(filename)
        root = bodyTree.getroot()

        logFile = root.get('log')
        if logFile is not None:
               logger = logging.getLogger("Quadsim")
               hndlr = logging.FileHandler(logFile, mode='w')
               hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
               logger.addHandler(hndlr)

        sim = SimulationManager(1.0/30)
        e = sim.physicalEnvironment
        cr = ConfigReader(e) # TODO: these should all be class methods...?
        
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
                e.addField(name, f)
            except AttributeError:
                pass # TODO: log an error?

        # now read the layout file
        layout = root.find('layout')
        layoutFile = layout.attrib['file']
        startSpace = cls._extractListStr(layout.find('startRegion').text)
        startSpace = [float(p) for p in startSpace]

        walls = cr.readLayoutFile(layoutFile)
        for w in walls:
            e.addObject(w)

        # now add the devices
        slack = 0.1
        randomHalf = lambda c: uniform(-c/2.0 + slack, c/2.0 - slack)
        deviceTypes = root.findall('device')
        for dv in deviceTypes:
            bodyFile = dv.findtext('body')
            programFile = dv.findtext('program')
            namePrefix = dv.attrib.get('namePrefix', 'Device')
            sensorSpecs = dv.findall('sensor')
            sensorList = {}
            for s in sensorSpecs:
                className = s.attrib['class']
                try:
                    sensorClass = getattr(sensors, className)
                    name = s.attrib['name']
                    # TODO: parse teh params
                    sensorList[name] = sensorClass
                except AttributeError:
                    pass
            nDevices = int(dv.findtext('count', 1))
            for i in range(nDevices):
                deviceBody = cr.readBodyFile(bodyFile)
                # todo: what about teh program
                devName = '{}_{:3d}'.format(namePrefix, i)
                deviceBody.name = devName
                for sn, s in sensorList.items():
                    deviceBody.addSensor(sn, s(deviceBody, {}))
                e.addObject(deviceBody)
                pos = [randomHalf(p) for p in startSpace]
                deviceBody.setPosition(pos)

        return sim




        







        
                    

            



