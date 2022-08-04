<h1>Generate random flows</h1>

Use the **randomTrips** application to generate random traffic (flows) for a network.

You can either:
    
  1. Use bash to generate the flows file directly; or
  2. Use bash to generate a configuration file for the flows.

---

Table of Contents
- [Create a flows configuration file](#create-a-flows-configuration-file)
  - [Example](#example)
- [Generate flows from a configuration file](#generate-flows-from-a-configuration-file)
  - [Example](#example-1)
- [What is RandomTrips.py?](#what-is-randomtripspy)

---

# Create a flows configuration file
With a configuration file, you can more easily reuse the same flows.

To generate a configuration file, simply append the `-C [FILE]` option to any **randomTrips.py** command that would otherwise generate the flows.

## Example
The following command generates a flows configuration to the file `config/flows.gcfg`.


```bash
python3 $SUMO_HOME/tools/randomTrips.py -n data/network.net.xml -o data/flows.xml --begin 0 --end 1 --flows 100 --jtrrouter --trip-attributes 'departPos="random" departSpeed='max'" --C config/flows.gcfg
```
- `-n data/network.net.xml` imports the network file titled **network.net.xml** from the **data** folder.
- `-o data/flows.xml` outputs the flow to a file titled **flows.xml** in the **data** folder.
- `--begin 0` initiates the flow at the start of the simulation.
- `--end 1` limits the number of vehicles per flow. Usually, flows define multiple vehicles, but in our case, a flow only defines 1 vehicle.
- `--flows 100` defines 100 vehicles.
- `--jtrrouter` is used to generate traffic without destinations.
- `--trip-attributes [str]` defines the attributes for each flow.
- `--C config/flows.gcfg` generates a configuration file titled **flows.flows.gcfg** in the **config** folder.

---

# Generate flows from a configuration file
Once you have a flows configuration file, you can call it using the `-c [FILE]` option with the following command to generate the actual flows file.

## Example
The following command generates a flows file based on the attributes provided within the flows configuration file titled `config/flows.gcfg`.

```bash
python3 $SUMO_HOME/tools/randomTrips.py -c config/flows.gcfg
```

---

# What is RandomTrips.py?
[randomTrips.py](https://sumo.dlr.de/docs/Tools/Trip.html#:~:text=%22randomTrips.py%22%20generates%20a,modified%20distribution%20as%20described%20below.) is an application that generates a set of random trips for a given network. It does so by choosing source and destination edge either uniformly at random or with a modified distribution.
