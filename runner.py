#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

from __future__ import absolute_import
from __future__ import print_function
import optparse
from termcolor import colored
import os
import subprocess
import sys

os.system('color')

# we need to import python modules from the $SUMO_HOME/tools directory
# If the the environment variable SUMO_HOME is not set, try to locate the python
# modules relative to this script
try:
    tools = os.path.join(os.environ['SUMO_HOME'], "tools")
    sys.path.append(tools)
except ImportError:
    sys.exit(colored("please declare environment variable 'SUMO_HOME'", "red"))

from sumolib import checkBinary  # noqa
import randomTrips  # noqa
import plot_trajectories  # noqa
netgenBinary = checkBinary('netgenerate')
jtrrouterBinary = checkBinary('jtrrouter')


def run():
    generate_network_file()

    generate_flows_file()

    generate_routes_files()

    run_simulation()

    # Generate edge data.
    # countEdgeUsageBinary = checkBinary('countEdgeUsage')
    # print("Computing edge-usage...")
    # call([countEdgeUsageBinary, "config/data/routes.xml", "-o", "output/data/countEdgeUsage.xml", "--intermediate"], stdout=DEVNULL, stderr=STDOUT)
    # print("Edge-usage computed.")

    process_conflicts()

    # generate_graphs()
    sys.stdout.flush()


def get_options():
    """Define options for this script and interpret the commandline."""
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of SUMO.")
    options, _ = optParser.parse_args()
    return options


def generate_network_file():
    """Use the network configuration file to generate the network file."""
    print(colored(">> Generating network...", "yellow"))
    call([netgenBinary, '-c', 'config/generators/network.netgcfg'],
         "Created network file.")


def call(args, successStr=""):
    response = subprocess.run(
        args, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if response.returncode == 0:
        msg = f"\t{colored('Success.', 'green')}\n"
        if (successStr):
            msg = f"\t{colored('Success >>', 'green')} {successStr}\n"

        print(msg)
        return response.stdout
    else:
        errors = "\n\t".join(response.stderr.split("\n"))
        print(
            f"\t{colored(errors, 'red')}\n")
        raise Exception("")


def generate_flows_file():
    """Use the flows configuration file to generate the flows file."""
    print(colored(">> Generating flow file...", "yellow"))
    call(["python", os.path.abspath(randomTrips.__file__), "-c",
         "config/generators/flows.flowsgcfg"], "Created flow file.")


def generate_routes_files():
    """Use the routes configuration file to generate the routes file."""
    print(colored(">> Generating routes file...", "yellow"))
    call([jtrrouterBinary, '-c', 'config/generators/routes.jtrrcfg'],
         "Created routes file.")


def run_simulation():
    """Run Sumo using the configuration file."""
    simulationDuration = '200'  # (seconds)
    print(colored(">> Running simulation...", "yellow"))
    res = call([sumoBinary, '-c', 'config/simulation/main.sumocfg',
                '-e', simulationDuration], "Simultion over.")
    if res:
        print(res)


def process_conflicts():
    import output.utils.xml_to_df as xml_to_df
    print(colored(">> Processing conflicts file...", "yellow"))
    # xml_to_df.main(xml_to_df.get_options([
    #     '--xml', 'output/data/ssm_reports.xml',
    #     '--cols', 'begin,end,foe,ego,time,type,value',
    #     '-o', 'output/data/conflicts.csv']))
    call(["python", os.path.abspath(xml_to_df.__file__), '--xml', 'output/data/ssm_reports.xml', '--cols', 'begin,end,foe,ego,time,type,value',
         '-o', 'output/data/conflicts.csv'], "Conflicts file processed.")

# def generate_graphs():
#   """Generate graphs based on the output FCD data."""
#   print(colored(">> Generating graphs...", "yellow"))
#   plot_trajectories.main(plot_trajectories.getOptions(["output/data/fcd.xml", "-c", "config/graphs/xpos_speed_trajectory.xml"]))
#   plot_trajectories.main(plot_trajectories.getOptions(["output/data/fcd.xml", "-c", "config/graphs/time_v_xpos_trajectory.xml"]))
#   plot_trajectories.main(plot_trajectories.getOptions(["output/data/fcd.xml", "-c", "config/graphs/time_v_speed_trajectory.xml"]))

#   print("Graphs generated.\n")


if __name__ == "__main__":
    # Load whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

run()
