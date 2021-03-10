# README #

This is a cyber-physical simulator for indoor sensor/actuator networks. 

## Introduction ##
The physical model includes the walls of the environment, large structures, and descriptions of the devices present. The physical device description specifies the device shape and size and body-relative location of sensors and actuators. The cyber model consists of simulated tasks running on the device, which take data from the sensors and send input to the actuators. The sensors and actuators are specified by Python classes named in the device description.

### How do I get set up? ###

You need Python 2.7 with the following modules:

* vPython (visual)
* [pyode](https://bitbucket.org/odedevs/ode/downloads)
* numpy

### Then what? ###

* Install the packages using pip/easy_install
* run sim.py

## Modelled sensing modalities
* Wave-based sensing (sound, radio)
* Motion/location sensing (proximity, acceleration)

