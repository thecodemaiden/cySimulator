from vtk import *
from environment import Environment
from wall import Wall
import logging
from random import uniform
from config_reader import ConfigReader
from object_types import Field    

if __name__ == '__main__':
    logger = logging.getLogger("Quadsim")
    hndlr = logging.FileHandler("sim.log", mode='w')
    hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
    logger.addHandler(hndlr)

    e = Environment()
    rf = Field(324, 1e-9)
    e.addField('RF', rf)
    cr = ConfigReader(e)

    layout_path = 'layout/example_layout.xml'
    quadcopter_body_path = 'bodies/quadcopter.xml'
    print('Room info read from {}'.format(layout_path))

    roomDims = [2,2,2]

    nq = raw_input('Number of quadcopters: ')
    try:
        nq = int(nq)
        if (nq < 0):
            raise ValueError
    except ValueError:
        nq = 5
        print("Defaulting to {} quadcopters".format(nq))

    for i in range(nq):
        name = 'Quad{}'.format(i)
        q = cr.readBodyFile(quadcopter_body_path)
        e.addObject(q)
        q.name = name
        x = uniform(-roomDims[0]/2 + .15, +roomDims[0]/2 - .15) # keep copters out of the walls
        y = uniform(-roomDims[1]/2 + .15, +roomDims[1]/2 - .15) # keep copters out of the walls
        z = uniform(-roomDims[2]/2 + .15, +roomDims[2]/2 - .15) # keep copters out of the walls
        q.setPosition((x,y,z))
        print('Copter at {}, {}, {}'.format(x,y,z))

    walls = cr.readLayoutFile(layout_path)
    for w in walls:
        e.addObject(w)
  

    e.start()

