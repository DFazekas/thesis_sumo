#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04


# TODO: Ensure this file isn't being used, then delete.


from __future__ import annotations
import optparse

from termcolor import colored
import os
import sys
from ..models.Simulation import Simulation


# Enables the Windows OS to apply color in their terminal.
os.system('color')

# we need to import python modules from the $SUMO_HOME/tools directory
# If the the environment variable SUMO_HOME is not set, try to locate the python
# modules relative to this script
try:
    tools = os.path.join(os.environ['SUMO_HOME'], "tools")
    sys.path.append(tools)
except ImportError:
    sys.exit(colored("please declare environment variable 'SUMO_HOME'", "red"))

# The origin and destination for the emergency vehicle.
# WARNING - Simulation will crash if these IDs don't exist on the network.
evOriginEdge, evDestEdge = 'B3B2', 'C1C0'


CvId = "C_Civilian"


def main(sumoBinary, demand, vtypeFilePath, runNum):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # FIXME - Code smell. May crash if the CWD isn't the root of main.py.
    # FIXME - Reruns are NOT randomly. They need to be.
    sim = Simulation(CvId)
    sim.run(sumoBinary, runNum, demand)

    sys.stdout.flush()


def get_options():
    """Define options for this script and interpret the commandline."""

    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of SUMO.")
    optParser.add_option("-r", "--runs", type="int", dest="runs", default=1,
                         help="How many reruns to simulate.")
    options, _ = optParser.parse_args()
    return options
