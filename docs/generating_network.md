<h1>Generate random network</h1>

Use the **netgenerate** application to generate a random network.

You can either:
    
  1. Use bash to generate the network file directly; or
  2. Use bash to generate a configuration file for the network.

---

Table of Contents
- [Create a network configuration file](#create-a-network-configuration-file)
  - [Example](#example)
- [Generate a network from a configuration file](#generate-a-network-from-a-configuration-file)
  - [Example](#example-1)

---

## Create a network configuration file
With a configuration file, you can more easily reuse the same network.

To generate a configuration file, simply append the `-C [FILE]` option to any **netgenerate** command that would otherwise generate the network.

### Example
The following command generates a network configuration to the file `config/network.netgcfg`.

```bash
netgenerate --grid --grid.number=10 -o ../data/network.net.xml -C config/network.netgcfg
```

Where:
- `--grid` defines a grid-shaped network.
- `--grid.number=10` defines a 10x10 grid-shaped network.
- `-o ../data/network.net.xml` outputs the generated network to a file titled **network.net.xml** in the **data** folder.
- `-C config/network.netgcfg` outputs the configuration to a file titled **network.netgcfg** in the **config** folder.

---

## Generate a network from a configuration file

Once you have a network configuration file, you can call it using the `-c [FILE]` option with the following command to generate the actual network file.

### Example
The following command generates a network file based on the attributes provided within the network configuration file titled `config/network.netgcfg`.

```bash
netgenerate -c config/network.netgcfg
```