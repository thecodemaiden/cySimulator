from vtk import *
from quad import Quadcopter
from environment import Environment
import logging

if __name__ == '__main__':
    logger = logging.getLogger("Quadsim")
    hndlr = logging.FileHandler("sim.log", mode='w')
    hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
    logger.addHandler(hndlr)

    e = Environment()

    q = Quadcopter(1,1, 0.1, 0.1, 0.4, e)
    e.addObject(q)
    e.start()

