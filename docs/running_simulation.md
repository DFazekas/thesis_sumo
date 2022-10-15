# Running the Simulation

To simplify running a SUMO simulation, we've written a script to handle importing and configuring all the necessary files.

By executing the following command, SUMO will open in a GUI window and automatically start the simulation. The characteristics of the network and traffic demand are described in external files. The window will automatically close upon completion, and recorded data will be exported into respective data files.

```bash
sumo-gui --net-file="config/grid.net.xml" --route-files="config/trips.trips.xml" --additional-files="config/vehicleTypes.add.xml" --delay=100 --gui-settings-file="config/viewSettings.xml" --device.ssm.file="output/data/ssm.xml" --start --quit-on-end --verbose --lateral-resolution=0.1 --human-readable-time=true
```

where:

- `--net-file=[FILE]` imports the network.
- `--route-files=[FILE]` imports the traffic demand.
- `--additional-files=[FILE]` imports the custom vehicle types.
- `--delay=[INT]` controls the speed of the simulation.
- `--gui-settings-file=[FILE]` imports GUI configurations.
- `--device.ssm.file=[FILE]` defines the SSM output data file.
- `--start` enables the GUI simulation to automatically start
- `--quit-on-end` enables the GUI window to automatically close upon complete.
- `--verbose` prints detailed console logs.
- `--lateral-resolution=[FLOAT]` enables sub-lane model and defines the width of each sub-lane.
- `--human-readable-time=[TRUE]` enables human-readable time output.
