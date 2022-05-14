# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

from __future__ import absolute_import
from __future__ import print_function
import optparse
from termcolor import colored

import os
from subprocess import call
import sys

# we need to import python modules from the $SUMO_HOME/tools directory
# If the the environment variable SUMO_HOME is not set, try to locate the python
# modules relative to this script
try:
    tools = os.path.join(os.environ['SUMO_HOME'], "tools")
    sys.path.append(tools)
except ImportError:
    sys.exit(colored("please declare environment variable 'SUMO_HOME'", "red"))

from sumolib import checkBinary # noqa
import randomTrips # noqa
import plot_trajectories # noqa
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
  # call([countEdgeUsageBinary, "config/data/routes.xml", "-o", "output/data/countEdgeUsage.xml", "--intermediate"])
  # print("Edge-usage computed.")

  generate_graphs()
  sys.stdout.flush()


def get_options():
  """Define options for this script and interpret the commandline."""
  optParser = optparse.OptionParser()
  optParser.add_option("--nogui", action="store_true", default=False, help="run the commandline version of SUMO.")
  options, args = optParser.parse_args()
  return options


def generate_network_file():
  """Use the network configuration file to generate the network file."""
  print(colored(">> Generating network...", "yellow"))
  retCode = call([netgenBinary, '-c', 'config/generators/network.netgcfg'], stdout=sys.stdout, stderr=sys.stderr)
  print(f"Network file closed with status: ({retCode}).\n")

def generate_flows_file():
  """Use the flows configuration file to generate the flows file."""
  print(colored(">> Generating flow file...", "yellow"))
  retCode = randomTrips.main(randomTrips.get_options([
    "-c", "config/generators/flows.flowsgcfg"
  ]))
  print(f"Flow file closed with status: ({retCode}).\n")

def generate_routes_files():
  """Use the routes configuration file to generate the routes file."""
  print(colored(">> Generating routes file...", "yellow"))
  retCode = call([jtrrouterBinary, '-c', 'config/generators/routes.jtrrcfg'], stdout=sys.stdout, stderr=sys.stderr)
  print(f"Routes file closed with status: ({retCode}).\n")

def run_simulation():
  """Run Sumo using the configuration file."""
  simulationDuration = '200' # (seconds)
  print(colored(">> Running simulation...", "yellow"))
  retCode = call([sumoBinary, '-c', 'config/simulation/main.sumocfg', '-e', simulationDuration], stdout=sys.stdout, stderr=sys.stderr)
  print(f"Simulation closed with status: ({retCode}).\n")

def generate_graphs():
  """Generate graphs based on the output FCD data."""
  print(colored(">> Generating graphs...", "yellow"))
  plot_trajectories.main(plot_trajectories.getOptions(["output/data/fcd.xml", "-c", "config/graphs/xpos_speed_trajectory.xml"]))
  plot_trajectories.main(plot_trajectories.getOptions(["output/data/fcd.xml", "-c", "config/graphs/time_v_xpos_trajectory.xml"]))
  plot_trajectories.main(plot_trajectories.getOptions(["output/data/fcd.xml", "-c", "config/graphs/time_v_speed_trajectory.xml"]))
  print("Graphs generated.\n")


if __name__ == "__main__":
  # Load whether to run with/without GUI.
  options = get_options()

  if options.nogui:
    sumoBinary = checkBinary('sumo')
  else:
    sumoBinary = checkBinary('sumo-gui')

run()