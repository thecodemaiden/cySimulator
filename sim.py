import logging
from config_reader import ConfigReader
from vpyViz.ode_visualization import Vpy_Visualization
from environment import SimulationManager
from time import time, sleep

logger = logging.getLogger("PEI Lab cySimulator")
logger.setLevel(logging.INFO)


def runSimulationFile(filename, withViz, timeout=None):
    sim = ConfigReader.readSimulationFile(filename)
    if withViz:
        sim.setVisualizer(Vpy_Visualization)
        scene = sim.visualizer.canvas
        scene.autoscale = False
        scene.autocenter =False
        scene.center = (0,-0.7, 0)

    sim.start()
    print('Simulation start')

    start = time()
    sim.runloop(timeout)
    realTime = time()-start
    simTime = sim.time

    if withViz:
        logger.info('FPS: {}'.format(sim.visualizer.fpsValues)) 

    del sim
    return (simTime, realTime)

if __name__ == '__main__':
    runSimulationFile('ray_test.xml', False, None)



