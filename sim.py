from vtk import *
from quad import Quadcopter
from environment import Environment
from wall import Wall
import logging
from random import uniform
from config_reader import ConfigReader

def parse_room_dimen(desc_str):
    desc_str.replace(" ", "")
    desc_str = desc_str.lower()
    nums = desc_str.split('x')[0:3] # limit to 3 vals
    dims = [2,2,2] # default values
    
    for i, n in enumerate(nums):
        try:
            dims[i] = float(n)
        except ValueError:
            pass

    return dims
    

if __name__ == '__main__':
    logger = logging.getLogger("Quadsim")
    hndlr = logging.FileHandler("sim.log", mode='w')
    hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
    logger.addHandler(hndlr)

    e = Environment()
    layout_path = 'config/layout/example_layout.xml'

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
        q = Quadcopter(.1,.1, 0.01, 0.01, 0.06, e)
        e.addObject(q)
        q.name = name
        x = uniform(-roomDims[0]/2 + .15, +roomDims[0]/2 - .15) # keep copters out of the walls
        y = uniform(-roomDims[1]/2 + .15, +roomDims[1]/2 - .15) # keep copters out of the walls
        z = uniform(-roomDims[2]/2 + .15, +roomDims[2]/2 - .15) # keep copters out of the walls
        q.setPosition((x,y,z))
        print('Copter at {}, {}, {}'.format(x,y,z))

    cr = ConfigReader(e)
    walls = cr.readLayoutFile(layout_path)
    for w in walls:
        e.addObject(w)
  

    e.start()

