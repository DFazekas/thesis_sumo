# Getting Started

Table of Contents
- [Getting Started](config/docs/getting_started.md)
- [Generating a network](config/docs/generating_network.md)
- [Generating flows](config/docs/generating_flows.md)
- [Generating routes](config/docs//generating_routes.md)
- [Running the simulation](config/docs/running_simulation.md)
- [Visualizing the data](config/docs/visualizing_data.md)

---

## Putting it all together
Once you have a network and routes file in the **data** folder, all you need is a configuration file for the simulation that calls upon them.

Create a file in the **config** directory titled **config.sumocfg** and paste the following configuration into it.
```xml
<configuration>
  <input>
    <net-file value="../data/network.net.xml" />
    <route-files value="../data/routes.xml" />
  </input>
</configuration>
```
Then open SUMO-GUI, click `File > Open Simulation` and select the file **config.sumocfg**. 



---

