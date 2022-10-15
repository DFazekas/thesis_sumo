#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

from __future__ import annotations
import optparse
import random
from termcolor import colored
import os
import sys
from config.simulation.Simulation import Simulation
from sumolib import checkBinary


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

# The insertion time for EV is random.
evInsertionTime = random.randint(12, 20)


CvId = "C_Civilian"


def main(sumoBinary, runs):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # FIXME - Code smell. May crash if the CWD isn't the root of main.py.
    # FIXME - Reruns are NOT randomly. They need to be.
    sim = Simulation(CvId)
    sim.run(sumoBinary, runs)

    # TODO: Inject a single EV. Can't use the distribution for the other civilian vehicles.

    # Convert ssm reports from XML format into CSV format.
    # runner.process_conflicts.main(
    #     inputFilePath=f"{dir}/output/data/ssm_reports.xml",
    #     outputFilePath=f"{dir}/output/data/conflicts.csv")

    # Generate graphs from ssm reports (CSV format).
    # TODO: These files won't exist until after runtime.
    # files = [
    #     "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\case_studies\\case_study_01\\scenario_01\\output\\data\\conflicts_2022_08_04-18_21_15.csv",
    #     "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\case_studies\\case_study_01\\scenario_01\\output\\data\\conflicts_2022_08_04-18_29_26.csv",
    #     "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\case_studies\\case_study_01\\scenario_01\\output\\data\\conflicts_2022_08_04-18_29_59.csv"
    # ]
    # runner.generate_graphs.main(
    #     inputFilePaths=files,
    #     outputFilePath=f"{dir}/output/graphs/heatmap.png"
    # )

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


if __name__ == "__main__":
    # Decide whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    main(sumoBinary, options.runs)

else:
    sumoBinary = checkBinary('sumo-gui')
    main(sumoBinary)
