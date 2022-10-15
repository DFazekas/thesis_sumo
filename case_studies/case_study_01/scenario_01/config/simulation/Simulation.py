import os
import traci
import subprocess
from .Vehicle import Vehicle, EmergencyVehicle
from .Detour import Detour
import randomTrips


class Simulation:

    def __init__(self, cvID) -> None:
        # The vehicle type ID for CVs.
        self.cvId = cvID
        # List of vehicles currently on the network.
        self.allVehicles: set[Vehicle] = set()
        # List of CVs.
        self.connectedVehicles: set[Vehicle] = set()
        # Reference to the EV.
        self.emergencyVehicle: EmergencyVehicle = None
        # List of halting vehicles.
        self.haltingVehicles: set[Vehicle] = set()

    def start(self, sumoBinary, suffix) -> None:
        """Starts the simulation."""
        dir = os.path.dirname(__file__)
        traci.start(
            [
                sumoBinary,
                '--net-file', f'{dir}/../data/grid.net.xml',
                '--route-files', f'{dir}/../data/trips.trips.xml',
                '--additional-files', f'{dir}/../data/vehicleTypes.add.xml',
                '--gui-settings-file', f'{dir}/../data/viewSettings.xml',
                '--device.ssm.file', f'{dir}/../../output/data/ssm_{suffix}.xml',
                '--start',
                '--quit-on-end',
                '--verbose',
                '--lateral-resolution', '0.1',
                '--human-readable-time', 'true',
                '--delay', '100',
                # '--step-method.ballistic', 'true'
            ])

    def run(self, sumoBinary, runs) -> None:
        """Manages the starting, running, and stopping of the simulation.

        Args:
            sumoBinary (_type_): _description_
            runs (_type_): _description_
        """

        for runNum in list(range(runs)):
            # Generate random trips. The output file should be placed in the /data folder.
            subprocess.run(["python", randomTrips.__file__,
                           "-c", "config/generators/trips.cfgtrips.xml"])

            self.start(sumoBinary, runNum)
            while self.shouldContinue():
                # Refresh the list of vehicles currently on the network.
                # FIXME: code smell - multiple subscriptions to the EV.
                self.updateVehicleList()

                # Rerouting is only necessary while EVs are actively on the network.
                if self.emergencyVehicle != None:
                    # Find all vehicles with common edges in their route. Detour them all.
                    evFutureRoute = self.emergencyVehicle.getFutureRoute()
                    Detour.detourVehicles(
                        self.connectedVehicles, evFutureRoute)

                # TODO: Revert detours once EV leaves network.
                self.updateHaltedVehicleList()
                self.stepForward()

            self.stop()

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
            veh for veh in self.allVehicles if veh.type == self.cvId]

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
            self.resumeVehicles(self.haltingVehicles)

        # There is an EV on the network. Halt all nearby vehicles.
        else:
            # Halt new nearby vehicles.
            vehiclesToHalt = self.emergencyVehicle.getVehiclesToHalt(
                self.haltingVehicles)
            self.haltVehicles(vehiclesToHalt)

            # Stop halting far away halted vehicles.
            vehiclesToResume = self.emergencyVehicle.getVehiclesToResume(
                self.haltingVehicles)
            self.resumeVehicles(vehiclesToResume)

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
