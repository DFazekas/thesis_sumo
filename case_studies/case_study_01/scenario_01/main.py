#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
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


def main(runner, sumoBinary):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""
    dir = os.path.dirname(__file__)
    networkFile = f'{dir}/config/data/simple_grid.net.xml'

    # Generate network file from config generator.
    # runner.generate_network_file.main(
    #     configFilePath=f'{dir}/config/generators/network.netgcfg',
    #     outputFilePath=f'{dir}/config/data/network.net.xml'
    # )

    # Generate flows file from config generator.
    runner.generate_flows_file.main(
        configFilePath=f"{dir}/config/generators/flows.flowsgcfg",
        networkFilePath=networkFile,
        outputFilePath=f'{dir}/config/data/flows.xml'
    )

    # Generate routes file from config generator.
    runner.generate_routes_files.main(
        configFilePath=f'{dir}/config/generators/routes.jtrrcfg',
        networkFilePath=networkFile,
        routesFilePath=f'{dir}/config/data/flows.xml',
        vehicleTypeFilePath=f'{dir}/config/generators/vehicleTypes.add.xml',
        outputFilePath=f'{dir}/config/data/routes.xml'
    )

    # Run simulation.
    # TODO: Code smell - relative paths used. Should use dependency injection.
    runner.run_simulation.main(
        sumoBinary, f'{dir}/config/simulation/main.sumocfg',
        [
            "-X", "always",
            "-n", networkFile,

        ])

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
