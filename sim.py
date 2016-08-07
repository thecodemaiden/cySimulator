from wall import Wall
import logging
from random import uniform
from config_reader import ConfigReader
from field_types import VectorField, SemanticField   
from visual import scene, rate
from vpyViz.ode_visualization import Vpy_Visualization
from environment import PhysicalEnvironment, SimulationManager

if __name__ == '__main__':
    logger = logging.getLogger("Quadsim")
    hndlr = logging.FileHandler("sim.log", mode='w')
    hndlr.setFormatter(logging.Formatter(fmt='%(name)s[%(levelname)s]: %(message)s'))
    logger.addHandler(hndlr)
    logger.setLevel(logging.ERROR)

    sim = SimulationManager(1.0/30)
    e = sim.physicalEnvironment
    sim.setVisualizer(Vpy_Visualization)
    v = sim.visualizer
  
    rf = VectorField(1, 1e-9)
    e.addField('RF', rf)

    rf_ez = SemanticField(3e8,1e-9)
    e.addField('RF_Semantic', rf_ez)
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
        logger.debug('Copter at {}, {}, {}'.format(x,y,z))

    walls = cr.readLayoutFile(layout_path)
    for w in walls:
        e.addObject(w)

    sim.start()

    scene.mouse.getclick()
    scene.autoscale = False
    sim.runloop()
 



