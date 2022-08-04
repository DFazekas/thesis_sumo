<h1>Visualization</h1>

Table of Contents
- [Prerequisites](#prerequisites)
- [Filter Data](#filter-data)
  - [Generate **edges.txt**](#generate-edgestxt)
- [Visualize Traffic Trajectories](#visualize-traffic-trajectories)

---

## Prerequisites
SUMO no longer provides the `matplotlib` application required for visualizing data. You'll need to install it manually.

Assuming you have `pip` installed and up-to-date, the following command may suffice:

```bash
pip3 install matplotlib
```

If pip is installed but out-dated, the following command may suffice in updating it:

```bash
python3 -m pip install --upgrade pip
```

## Filter Data
By default, the simulation outputs FCD data for all edges on the network. Trying to visualize this may be overwhelming for large networks.

To filter the FCD output data to specific edges/lanes, you'll need to:
1. List the desired lane IDs in the file **config/graphs/edges.txt** (*this can be generated as discussed below*). 
2. Enable filtering of the output in the **config/simulation/main.sumocfg** file; scroll down to the `output` section and follow the instructions written there.

### Generate **edges.txt**
You can leverage **netedit** to generate the **edges.txt** file using the following steps:

1. Open the network in **netedit**.
2. Enter *lane selection* mode by pressing `s`.
3. Select only the lanes of interest.
4. In the left panel, scroll down to *selection operations* and click "save"; saving the file as **edges.txt** in the **data** folder.
  
    `NOTE:` If you choose to name it differently or elsewhere, you'll need to change its reference in the **config/config.sumocfg** file.

## Visualize Traffic Trajectories
The following command will generate the configuration file, titled **config/graphs/xpos_time_trajectory.xml** for visualizing a "X-Position Vs. Time" graph from the **output/fcd.xml** file. 
```bash
python3 $SUMO_HOME/tools/plot_trajectories.py -t xs -o graphs/xpos_speed_trajectory --label "X-Position Vs. Speed" --legend -C config/graphs/xpos_speed_trajectory.xml
```
where:
- `-t xs` defines the plot type to be x-position versus speed.
- `--legend` adds a legend.
- `--label "X-Position Vs. Speed"` adds the label "X-Position Vs. Speed" to the graph.
- `-o graphs/xpos_time_trajectory` outputs the graph titled **xpos_speed_trajectory.png** to the **graphs** folder.
- `-C config/graphs/xpos_speed_trajectory.xml` outputs this script as a configuration file titled **xpos_speed_trajectory.xml** in the **config/graphs** folder.


Once you have the configuration file, you can generate the graph using the following command. **NOTE:** you must provide the data to visualize--in our case, it's **output/fcd.xml**.
```bash
python3 $SUMO_HOME/tools/plot_trajectories.py output/fcd.xml -c config/graphs/xpos_speed_trajectory.xml
```