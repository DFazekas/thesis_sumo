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
import traci.constants as tc

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


CV_id = "C_Civilian"
# List of currently halted vehicles.
haltedVehicles: set[Vehicle] = set()


def main(sumoBinary):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""
    sim = Simulation()

    sim.start(sumoBinary)
    while sim.shouldContinue():
        # Refresh the list of vehicles currently on the network.
        # FIXME: code smell - multiple subscriptions to the EV.
        sim.updateVehicleList()

        # Rerouting is only necessary while EVs are actively on the network.
        if sim.emergencyVehicle != None:
            # Find all vehicles with common edges in their route. Detour them all.
            evFutureRoute = sim.emergencyVehicle.getFutureRoute()
            Detour.detourVehicles(sim.connectedVehicles, evFutureRoute)

        # TODO: Revert detours once EV leaves network.
        sim.updateHaltedVehicleList()
        sim.stepForward()

    sim.stop()

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


class Simulation:

    def __init__(self) -> None:
        # List of vehicles currently on the network.
        self.allVehicles: set[Vehicle] = set()
        # List of CVs.
        self.connectedVehicles: set[Vehicle] = set()
        # Reference to the EV.
        self.emergencyVehicle: EmergencyVehicle = None
        # List of halting vehicles.
        self.haltingVehicles: set[Vehicle] = set()

    def start(self, sumoBinary) -> None:
        """Starts the simulation."""
        dir = os.path.dirname(__file__)
        traci.start(
            [
                sumoBinary,
                '--net-file', f'{dir}/config/data/network.net.xml',
                '--route-files', f'{dir}/config/data/trips.trips.xml',
                '--additional-files', f'{dir}/config/generators/vehicles.add.xml',
                '--delay', '200',
                '--gui-settings-file', f'{dir}/config/simulation/viewSettings.xml',
                '--device.ssm.file', f'{dir}/output/data/ssm.xml',
                '--start',
                '--quit-on-end',
                '--verbose',
                '--lateral-resolution', '1'
            ])

    def shouldContinue(self) -> bool:
        """Checks that the simulation should continue running.

        Returns:
            bool: `True` if vehicles exist on network. `False` otherwise.
        """
        numVehicles = traci.simulation.getMinExpectedNumber()
        return True if numVehicles > 0 else False

    def stepForward(self) -> None:
        """Moves the simulation clock by one second."""
        traci.simulationStep()

    def stop(self) -> None:
        """Stops the simulation."""
        traci.close()

    def updateVehicleList(self) -> None:
        """Updates the list of vehicles on the network."""

        # Update list of all vehicles.
        self.allVehicles = self.getActiveVehicles()

        # Filter for only CVs.
        self.connectedVehicles = [
            veh for veh in self.allVehicles if veh.type == CV_id]

        # Filter for the one EV.
        ev = next(
            filter(lambda veh: veh.id == 'EV', self.allVehicles), None)
        self.emergencyVehicle = None if ev is None else EmergencyVehicle(ev.id)

    def getActiveVehicles(self) -> set[Vehicle]:
        """Returns the list of all active vehicles on the network.

        Returns:
            set[Vehicle]: List of vehicles.
        """
        activeVehsIds = traci.vehicle.getIDList()
        return [Vehicle(id) for id in activeVehsIds]

    def updateHaltedVehicleList(self) -> None:
        """Halts all vehicles surrounding the EV, and resumes speed once out of range."""

        # There is no EV on the network. Resume speeds of all halting vehicles.
        if self.emergencyVehicle is None:
            print("No EV found.")
            self.resumeVehicles(self.haltingVehicles)

        # There is an EV on the network. Halt all nearby vehicles.
        else:
            print(f"Time: {traci.simulation.getTime()}")

            # Halt new nearby vehicles.
            vehiclesToHalt = self.emergencyVehicle.getVehiclesToHalt(
                self.haltingVehicles)
            print(f"\tHalted vehicles (before): {self.haltingVehicles}")
            print(f"\tVehicles to halt: {vehiclesToHalt}")
            self.haltVehicles(vehiclesToHalt)

            # Stop halting far away halted vehicles.
            vehiclesToResume = self.emergencyVehicle.getVehiclesToResume(
                self.haltingVehicles)
            print(f"\tVehicles to resume: {vehiclesToResume}")
            self.resumeVehicles(vehiclesToResume)

            print(f"\tHalted vehicles (after): {self.haltingVehicles}")

    def haltVehicles(self, vehicles: set[Vehicle]) -> None:
        """Halts all provided vehicles.

        Args:
            vehicles (set[Vehicle]): The vehicles to halt.
        """
        vehiclesToHalt = vehicles.copy()
        newSpeed = 0
        for veh in vehiclesToHalt:
            veh.setSpeed(newSpeed)
            self.haltingVehicles.add(veh)

    def resumeVehicles(self, vehicles: set[Vehicle]) -> None:
        """Resumes driving of halted vehicles.

        Args:
            vehicle (set[Vehicle]): List of vehicles to resume driving.
        """
        vehiclesToResume = vehicles.copy()
        for veh in vehiclesToResume:
            # If vehicle left the network, setSpeed will cause an error.
            if veh.isActive(self.allVehicles):
                newSpeed = -1  # Returns speed regulation control to TraCI.
                veh.setSpeed(newSpeed)
                # FIXME: smell - is removing objs from list that easy?
            self.haltingVehicles.remove(veh)


class Detour:
    # TODO: track modified routes, and allow reverting.
    def detourVehicles(vehicles: set[Vehicle], evRoute: set[str]):
        """Reroutes all vehicles whose route shares edges with the EV route.

        Args:
            vehicles (set[Vehicle]): The vehicles to reroute.
            evRoute (set[str]): The route of the EV.
        """
        # FIXME: Roads of opposite directions are considered different edges, and thus can't simply be compared for incoming traffic. If I want to reserve the entire road, I'll need an alternative approach.

        # Go through routes of each CV. Compare against EV.
        for veh in vehicles:
            futureRoute = veh.getFutureRoute()
            sharedEdges = [
                cvEdge for cvEdge in futureRoute if cvEdge in evRoute]

            # Increase travel time for all shared roads.
            for edgeId in sharedEdges:
                print(
                    f"Vehicle ({veh.id}) has shared edges with EV: {sharedEdges}")
                veh.setAvoidEdge(edgeId)

            # Recalculate route, if necessary.
            if sharedEdges:
                veh.recalculateRoute()


class Vehicle:
    def __init__(self, id: str):
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

    def setSpeed(self, speed: float) -> None:
        """Sets the vehicle's speed to a constant value.

        Args:
            speed (float): The new speed.
        """
        traci.vehicle.setSpeed(self.id, speed)

    def setAvoidEdge(self, edgeId: str):
        """Sets the travel time for the vehicle to infinity.

        Args:
            edgeId (str): The edge to avoid.
        """
        traci.vehicle.setAdaptedTraveltime(
            self.id, edgeId, float('inf'))

    def recalculateRoute(self):
        """Recalculates the vehicle's route based on edge travel times."""
        traci.vehicle.rerouteTraveltime(self.id)

    def isActive(self, vehList: set[Vehicle]) -> bool:
        """Returns True if the vehicle is in the provided list. False otherwise.

        Args:
            vehList (set[Vehicle]): List of vehicles to search through.

        Returns:
            bool: Whether the vehicle is in the list or not.
        """
        return self.id in (veh.id for veh in vehList)

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


class EmergencyVehicle(Vehicle):

    def __init__(self, id: str) -> None:
        super().__init__(id)

        # Listen for surrounding vehicles.
        self.subscribeToEV()
        self.nearbyVehicles: set[Vehicle] = self.findNearbyVehicles()

    def subscribeToEV(self) -> None:
        """Subscribes to the vehicular context of the Emergency Vehicle."""
        # Listen for distances of all vehicles near the EV.
        objectId = self.id
        contextDomain = tc.CMD_GET_VEHICLE_VARIABLE
        contextRange = 0
        variablesToReturn = [tc.VAR_DISTANCE]
        traci.vehicle.subscribeContext(
            objectId, contextDomain, contextRange, variablesToReturn)

        # Filter for vehicles on and neighbouring the lane of the EV.
        traci.vehicle.addSubscriptionFilterLCManeuver(
            downstreamDist=10, upstreamDist=10)

    def findNearbyVehicles(self) -> set[Vehicle]:
        """Returns a list of vehicles within range of the EV.

        Returns:
            set[Vehicle]: Nearby vehicles.
        """
        subResults = traci.vehicle.getContextSubscriptionResults(
            self.id)

        nearbyVehicles = [Vehicle(id)
                          for id in list(subResults.keys())]
        return nearbyVehicles

    def getVehiclesToResume(self, haltedVehicles: set[Vehicle]) -> set[Vehicle]:
        """Retuns a set of vehicles to stop halting.

        Args:
            nearbyVehicles (set[Vehicle]): Set of nearby vehicles.
            haltedVehicles (set[Vehicle]): Set of halted vehicles

        Returns:
            set[Vehicle]: Set of vehicles to stop halting.
        """

        vehiclesToResume = set()
        for haltedVeh in haltedVehicles:
            if haltedVeh.id not in (nearbyVeh.id for nearbyVeh in self.nearbyVehicles):
                vehiclesToResume.add(haltedVeh)
        return vehiclesToResume

    def getVehiclesToHalt(self, haltedVehicles: set[Vehicle]) -> set[Vehicle]:
        """Returns a list of vehicles to halt.

        Args:
            nearbyVehicles (set[Vehicle]): List of nearby vehicles.
            haltingVehicles (set[Vehicle]): List of already halted vehicles.

        Returns:
            set[Vehicle]: List of vehicles to halt.
        """

        vehiclesToHalt = set()
        for nearbyVeh in self.nearbyVehicles:
            if nearbyVeh.id not in (haltedVeh.id for haltedVeh in haltedVehicles):
                vehiclesToHalt.add(nearbyVeh)
        return vehiclesToHalt


if __name__ == "__main__":
    # Decide whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    main(sumoBinary)

else:
    sumoBinary = checkBinary('sumo-gui')
    main(sumoBinary)
