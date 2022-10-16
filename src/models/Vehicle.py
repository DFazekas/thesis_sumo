from __future__ import annotations
import traci
import traci.constants as tc


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
        Due to a bug, the EV will identify itself as a nearby vehicle. 
        Therefore, extra steps are taken to remove self inclusion in the output.

        Returns:
            set[Vehicle]: Nearby vehicles.
        """
        subResults = traci.vehicle.getContextSubscriptionResults(
            self.id)
        ids = set(subResults.keys())
        ids.discard('EV')

        nearbyVehicles = [Vehicle(id)
                          for id in list(ids)]
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
