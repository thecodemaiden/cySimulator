from vtk import *
from quad import Quadcopter
from environment import Environment
from wall import Wall
import logging

if __name__ == '__main__':
    logger = logging.getLogger("Quadsim")
    hndlr = logging.FileHandler("sim.log", mode='w')
    hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
    logger.addHandler(hndlr)

    e = Environment()
    q = Quadcopter(.1,.1, 0.01, 0.01, 0.06, e)
    e.addObject(q)

    r = Wall.makeRoom((3.0, 2.0, 3.0), (0,0,0), e)
    for wall in r:
        e.addObject(wall)

    e.start()

