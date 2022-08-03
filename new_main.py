#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
from sumolib import checkBinary  # noqa
import runner as rn

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


def main(sumoBinary):
    """Orchestrate the simulation of multiple case studies, each against multiple scenarios."""

    # Generate one network file per case study.
    # TODO: Create more networks.
    rn.generate_network_file.main(
        'config/generators/network.netgcfg',
        [
            "-o", "config/data/network_temp.net.xml"
        ])

    # rn.generate_flows_file.main("config/generators/flows.flowsgcfg")

    # rn.generate_routes_files.main('config/generators/routes.jtrrcfg')

    # rn.run_simulation.main(sumoBinary, 'config/simulation/main.sumocfg')

    # rn.process_conflicts.main()

    # These graphs require data from multiple simulation results.
    # rn.generate_graphs.main()

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
