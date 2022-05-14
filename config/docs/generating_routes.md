<h1>Generate random routes</h1>

Use the **jtrrouter** application to generate random routes based on the network and flow files.

---
Table of Contents
- [What is JtrRouter?](#what-is-jtrrouter)

---

```bash
jtrrouter -n ../data/network.net.xml -r ../data/flows.xml -o ../data/routes.xml -A -T "25,50,25" -C config/routes.jtrrcfg
```
Where:
- `-r flows.xml` inputs the *flows.xml* routes file.
- `-o routes.xml` outputs to the file titled *routes.xml*.
- `-A` enables **accept-all-destinations**;whether all edges are allowed as sink edges.
- `-T "25,50,25"` overwrites the turn defaults.
- `-C config/routes.jtrrcfg` generates a configuration file titled **routes.jtrrcfg** in the **config** folder.

Once you have a configuration file, you can generate the actual routes file by calling the following command:
```bash
jtrrouter -c config/routes.jtrrcfg
```

---

# What is JtrRouter?
[Jtrrouter](https://sumo.dlr.de/docs/jtrrouter.html) is a routing application which uses flows and turning percentages at junctions as input.

The following parameters must be supplied:
- the network to route the vehicles through.
- the description of the turning ratios for the junctions.
- the descriptions of the flows.