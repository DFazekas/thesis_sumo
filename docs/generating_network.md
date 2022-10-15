<h1>Generate random network</h1>

Networks are the cornerstone to SUMO simulations as they describe the physical roads that traffic drives on.

---

Table of Contents

- [Create a network](#create-a-network)
- [What is NetGenerate?](#what-is-netgenerate)

---

## Create a grid network

The following command generates a symmetric 4x4 grid network with 400 meter roads between each intersection. Each road has 2 lanes. Each outer edge has an attached road leading outside of the network to help SUMO identify fringes.

```bash
netgenerate --grid --grid.number=4 --grid.length=400 --grid.attach-length=100 --default.lanenumber=2 --fringe.guess=true --output-file="../data/grid.net.xml"
```

Where:

- `--grid` enables a grid-shaped network.
- `--grid.number=[INT]` defines the network size. Value `4` generates a 4x4 grid.
- `--grid.length=[FLOAT]` defines length of each edge, in meters.
- `default.lanenumber=[INT]` defines the number of lanes per edge.
- `--grid.attach-length=[FLOAT]` defines the length of attached edges (fringes), in meters.
- `--fringe.guess=[TRUE]` enables SUMO to automatically guess which edges are considered fringes.
- `--output-file=[FILE]` defines the output network file.

---

# What is NetGenerate?

[NetGenerate](https://sumo.dlr.de/docs/netgenerate.html) generates abstract road networks to be used by other SUMO applications.
