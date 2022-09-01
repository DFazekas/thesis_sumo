#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

from __future__ import annotations
import optparse
from termcolor import colored
import os
import sys
from sumolib import checkBinary
import traci

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

sumoBinary = checkBinary('sumo-gui')
CV_id = "C_Civilian"
connectedVehicles: list[Vehicle] = []
emergencyVehicle: Vehicle = None


def main():
    """Generates all prerequisite files to run the simulation, export data, and process the data."""
    global connectedVehicles, emergencyVehicle

    startSim()
    while shouldContinueSim():
        connectedVehicles, emergencyVehicle = updateVehicleList()

        # Rerouting is only necessary while EVs are actively on the network.
        if emergencyVehicle != None:
            evFutureRoute = emergencyVehicle.getFutureRoute()

            # Find all vehicles with common edges in their route. Detour them all.
            detourVehicles(connectedVehicles, evFutureRoute)

        traci.simulationStep()

    traci.close()
    # Generate flows file from config generator.
    # runner.generate_flows_file.main(
    #     configFilePath=f"{dir}/config/generators/flows.flowsgcfg",
    #     networkFilePath=networkFile,
    #     outputFilePath=f'{dir}/config/data/flows.xml'
    # )

    # Generate routes file from config generator.
    # runner.generate_routes_files.main(
    #     configFilePath=f'{dir}/config/generators/routes.jtrrcfg',
    #     networkFilePath=networkFile,
    #     routesFilePath=f'{dir}/config/data/flows.xml',
    #     vehicleTypeFilePath=f'{dir}/config/generators/vehicleTypes.add.xml',
    #     outputFilePath=f'{dir}/config/data/routes.xml'
    # )

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


def startSim():
    """Starts the simulation."""
    dir = os.path.dirname(__file__)
    traci.start(
        [
            sumoBinary,
            '--net-file', f'{dir}/config/data/network.net.xml',
            '--route-files', f'{dir}/config/data/trips.trips.xml',
            '--additional-files', f'{dir}/config/generators/vehicles.add.xml',
            '--delay', '400',
            '--gui-settings-file', f'{dir}/config/simulation/viewSettings.xml',
            '--device.ssm.file', f'{dir}/output/data/ssm.xml',
            '--start'
        ])


def shouldContinueSim() -> bool:
    """Checks that the simulation should continue running.

    Returns:
        bool: `True` if vehicles exist on network. `False` otherwise.
    """
    numVehicles = traci.simulation.getMinExpectedNumber()
    return True if numVehicles > 0 else False


def getActiveVehicles() -> list[Vehicle]:
    """Returns the list of all active vehicles on the network.

    Returns:
        list[Vehicle]: List of vehicles.
    """
    activeVehsIds = traci.vehicle.getIDList()
    return [Vehicle(id) for id in activeVehsIds]


def updateVehicleList() -> list[list[Vehicle], Vehicle]:
    """Returns list of active CVs and the ER, if any.

    Returns:
        [CVs, EV]: List of active CVs and EV.
    """
    # TODO: This function creates new Vehicles every time step. It might be optimal to only check for newly departed/arrived vehicles.
    allVehicles = getActiveVehicles()
    # Filter for only CVs.
    vehList = [veh for veh in allVehicles if veh.type == CV_id]
    # Filter for the one EV.
    emergencyVehicle = next(
        filter(lambda veh: veh.id == 'ER', allVehicles), None)
    return [vehList, emergencyVehicle]


def detourVehicles(vehicles: list[Vehicle], evRoute: list[str]):
    # FIXME: Roads of opposite directions are considered different edges, and thus can't simply be compared for incoming traffic. If I want to reserve the entire road, I'll need an alternative approach.

    # Go through routes of each CV. Compare against EV.
    for veh in vehicles:
        futureRoute = veh.getFutureRoute()
        commonEdges = [cvEdge for cvEdge in futureRoute if cvEdge in evRoute]

        # Increase travel time for all common roads.
        for edgeId in commonEdges:
            print(f"Vehicle ({veh.id}) has common edges: {commonEdges}")
            traci.vehicle.setAdaptedTraveltime(veh.id, edgeId, float('inf'))

        # Recalculate route.
        if commonEdges:
            traci.vehicle.rerouteTraveltime(veh.id)


def get_options():
    """Define options for this script and interpret the commandline."""

    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of SUMO.")
    options, _ = optParser.parse_args()
    return options


class Vehicle:
    def __init__(self, id):
        self._id = id
        self._vType = traci.vehicle.getTypeID(id)

    def __str__(self) -> str:
        return self._id

    def __repr__(self) -> str:
        return self._id

    def getPosition(self) -> int:
        '''
        Returns the vehicle's current index along their route.

            Returns:
                index (int): Index of current position on route.
        '''
        return traci.vehicle.getRouteIndex(self._id)

    def getRoute(self) -> list[str]:
        """Returns the vehicle's current route.

        Returns:
            Route (list[str]): The IDs of the edges the vehicle's is made of. 
        """
        return traci.vehicle.getRoute(self._id)

    def getFutureRoute(self) -> list[str]:
        """Returns the future route.

        Returns:
            list[str]: List of route edges not yet travelled. 
        """
        positionIndex = self.getPosition()
        route = self.getRoute()
        return route[positionIndex + 1:]

    @property
    def id(self) -> str:
        """Returns the vehicle's ID.

        Returns:
            str: ID of the vehicle.
        """
        return self._id

    @property
    def type(self) -> str:
        """Returns the ID of the vehicle's type.

        Returns:
            str: Vehicle type ID.
        """
        return self._vType


if __name__ == "__main__":
    # Decide whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    main(sumoBinary)
