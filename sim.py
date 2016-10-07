import logging
from config_reader import ConfigReader
from vpyViz.ode_visualization import Vpy_Visualization
from environment import SimulationManager
from time import time, sleep

logger = logging.getLogger("Quadsim")
logger.setLevel(logging.INFO)


def runSimulationFile(filename, withViz, timeout=None):
    sim = ConfigReader.readSimulationFile(filename)
    if withViz:
        sim.setVisualizer(Vpy_Visualization)
        scene = sim.visualizer.canvas
        #scene.autoscale = False
        #scene.autocenter =False

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

def benchmarkTest(countList, withViz=False, timeout=30.0):
    import xml.etree.ElementTree as etree
    tree = etree.parse('simple_setup.xml')
    root = tree.getroot()
    for quadCount in countList:
        # change the logfile
        logName = 'sim{:03d}_radio.log'.format(quadCount)
        root.set('log', logName)
        quadCountElem = root.find('device/count')
        quadCountElem.text = str(quadCount)
        print '--{}--'.format(quadCount)
        for i in range(20):
            sim = ConfigReader._loadSimulationConfig(root)
            if withViz:
                sim.setVisualizer(Vpy_Visualization)
                scene = sim.visualizer.canvas
                scene.autoscale = False
                scene.autocenter =False

            sim.start()
            print('Simulation start')

            start = time()
            sim.runloop(timeout)
            realTime = time()-start
            simTime = sim.time
            nColl = sim.nCollisions
            if withViz:
                logger.info('FPS: {}'.format(sim.visualizer.fpsValues)) 

            logger.info('Simulation time: {:4.2f}\t Clock time: {:4.2f}\t Collisions: {}'.format(simTime, realTime, nColl))
            logger.handlers = []
            del sim
   

   

if __name__ == '__main__':
    benchmarkTest([5, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200, 400, 800, 1500])
    #s,r = runSimulationFile('simple_setup.xml', False, 30.0)
    #print s,r
    #import visual as v
    #v.rate(1)
    # v.exit()



