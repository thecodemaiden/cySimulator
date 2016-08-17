from wall import Wall
import logging
from random import uniform
from config_reader import ConfigReader
from field_types import VectorField, SemanticField   
from vpyViz.ode_visualization import Vpy_Visualization
from environment import SimulationManager

from space_field import *

if __name__ == '__main__':
    logger = logging.getLogger("Quadsim")
    hndlr = logging.FileHandler("sim.log", mode='w')
    hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
    logger.addHandler(hndlr)
    logger.setLevel(logging.ERROR)

    sim = ConfigReader.readSimulationFile('sim_setup.xml')
    sim.setVisualizer(Vpy_Visualization)
    scene = sim.visualizer.canvas

    #shittyField = OdeField(340, sim.space)
    #shittyObject = OdeFieldTestObject()
    #sim.addField('Shitty', shittyField)
    #sim.addFieldObject('Shitty', shittyObject)

    sim.start()

    scene.autoscale = False
    scene.autocenter=False
    scene.mouse.getclick()

    sim.runloop()
 



