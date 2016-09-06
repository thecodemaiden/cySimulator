import logging
from config_reader import ConfigReader
from vpyViz.ode_visualization import Vpy_Visualization
from environment import SimulationManager
from time import time, sleep

logger = logging.getLogger("Quadsim")
logger.setLevel(logging.INFO)


def runSimulationFile(filename, withViz):
    sim = ConfigReader.readSimulationFile(filename)
    if withViz:
        sim.setVisualizer(Vpy_Visualization)
        scene = sim.visualizer.canvas
        scene.autoscale = False
        scene.autocenter =False

    sim.start()
    print('Simulation start')

    start = time()
    sim.runloop()
    realTime = time()-start
    simTime = sim.time

    if withViz:
        logger.info('FPS: {}'.format(sim.visualizer.fpsValues)) 

    del sim
    return (simTime, realTime)

if __name__ == '__main__':

    def benchmarkFile(filename):
        for i in range(10):
            doVis = False
            (s, r) = runSimulationFile(filename, doVis)
            logger.info('Simulation time: {:4.2f}\t Clock time: {:4.2f}'.format(s, r))
            logger.handlers = []
            sleep(1)
    #names = ['sim05_radio.xml','sim10_radio.xml','sim15_radio.xml','sim20_radio.xml','sim25_radio.xml']
    #for n in ['sim100_radio.xml']:
    #    print("\t--- {} ---\t". format(n))
    #    benchmarkFile('profile_setup/'+n)
    runSimulationFile('porter_hall_sim.xml', True)
    #import visual as v
    #v.rate(1)
   # v.exit()



