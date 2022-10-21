from .Vehicle import Vehicle

# List of currently halted vehicles.
haltedVehicles: set[Vehicle] = set()


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
                veh.setAvoidEdge(edgeId)

            # Recalculate route, if necessary.
            if sharedEdges:
                veh.recalculateRoute()
                print(f"\tAfter: {veh.getFutureRoute()}")
