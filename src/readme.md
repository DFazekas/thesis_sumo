# How to change CV penetration rate

To change the market penetration rate for CVs, modify two values in the _config/data/vehicleTypes.add.xml_ file. Specifically, the `probability` attribute on each of the two `civilianVehicles` types within the `vTypeDistribution` tag.

The sum of the two values should equal 100%.

# How to change traffic demand rate

To change the traffic demand (vehicles per hour), modify the _config/generators/trips.cfgtrips.xml_ file. Specifically, the value of the `insertion-rate` attribute.

If you use the _main.py_ file to run the simulation, the prerequisite trips file will be generated automatically before the start of each run. However, if you run SUMO directly (via GUI or CLI), you'll need to generate the trips file manually.

### Create trips file manually

To create the trips file manually, execute the following command:

```bash
randomtrips.py -c [FILE]
```

where `[FILE]` is the absolute path to the _config/generators/trips.cfgtrips.xml_ file.
