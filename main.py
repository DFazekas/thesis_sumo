#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
from sumolib import checkBinary  # noqa
from src.runner import run_simulation as rn

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


demands = [1000]  # vehicles per hour. [1000, 1500, 2000]
reruns = 1  # The number of times to rerun the same simulation


def main(sumoBinary):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # Get all penetration vType distribution files.
    path = "src/config/vTypes"
    fileNames = os.listdir(path)
    vTypeFile = [f'{path}/{name}' for name in fileNames]
    vTypeFiles = [vTypeFile[0]]

    # Run grid network x100 at 1000 veh/hr and 0% CVs, average the outputs, aggregrate the SSM data. Repeat for 25%, 50%, 75%, and 100% CVs. Repeat for 1500 veh/hr and 2000 veh/hr.
    # Expecting: 15 data files.

    for demand in demands:
        for vIndex, vTypeFile in enumerate(vTypeFiles):
            for runNum in list(range(reruns)):
                prefix = f"d{demand}_p{vIndex}_r{runNum}"
                rn.runGrid(sumoBinary, vTypeFile, demand, prefix)

    # Run real-world network x100 at 1000 veh/hr, average the outputs, aggregrate the SSM data. Repeat for 1500 veh/hr and 2000 veh/hr.
    # TODO: Add real-world case study.

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


def get_options():
    """Define options for this script and interpret the commandline."""

    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of SUMO.")
    options, _ = optParser.parse_args()
    return options


if __name__ == "__main__":
    # Decide whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    main(sumoBinary)
