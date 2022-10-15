<h1>Generate random trips</h1>

Use the **randomTrips** application to generate random vehicle trips for a network.

---

Table of Contents

- [Generate trips](#generate-trips)
  - [Example](#example-1)
- [What is RandomTrips.py?](#what-is-randomtripspy)

---

# Generate trips

As trips cite specific road IDs that must be matched in the network being used, the prerequisite is to **create a network file**. Optionally, you may wish for the generated vehicles to include custom vehicle types or distributions, in which case you'll also need to **create a vehicle type file**.

Once you have the prerequisite files you can generate random trips.

## Example

The following command generates a large number of vehicles following random trips. Each vehicle enters the network on the most available lane at a random outer edge, and leaves the network at a random outer edge at least 10000 meters from their origin. The type of vehicles used are defined in vehicle distribution in an external file.

```bash
randomTrips.py --net-file="grid.net.xml" --output-trip-file="trips.trips.xml" --trip-attributes='departPos="random" departSpeed="max" type="civilianVehicles" departLane="best"' --min-distance=1500 --allow-fringe --fringe-factor="10000" --insertion-rate=100
```

- `--net-file=[FILE]` imports the network file that the trips will be based on.
- `--output-trip-file=[FILE]` defines the output trip file.
- `--trip-attributes [STR]` defines the attributes for each vehicle. In our example, this includes:
  - `departPos=[STR]` defines where the vehicle shall enter the network. Value `"random"` randomly selects a street ensuring distributed street use.
  - `departSpeed=[STR]` defines the speed that the vehicle entering the network. Value `"max"` sets speed to maximum, ensures realistic speeds.
  - `departLane=[STR]` defines which lane the vehicle enters the network on. Value `"best"` selects an available lane.
  - `type=[STR]` defines the type of vehicle entering the network. Value `"civilianVehicles"` is a custom vehicle distribution defined in the "_vehicleTypes.add.xml_" file.
- `min-distance=[FLOAT]` defines the minimum allowed distance for the generated routes. A value greater than the average edge length ensures a multi-link route.
- `allow-fringe=[TRUE]` considers fringes (outer edges) in the origin/destination edge selection.
- ` fringe-factor=[FLOAT]` defines the probability that trips start/end on fringes. Large values virtually ensure that all vehicles trips start and end outside the network.
- `insertion-rate=[FLOAT]` defines how many vehicles per hour enter the network.

---

# What is RandomTrips.py?

[randomTrips.py](https://sumo.dlr.de/docs/Tools/Trip.html#:~:text=%22randomTrips.py%22%20generates%20a,modified%20distribution%20as%20described%20below.) is an application that generates a set of random trips for a given network. It does so by choosing source and destination edge either uniformly at random or with a modified distribution.
