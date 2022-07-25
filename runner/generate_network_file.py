from .utils import runPythonFile
from termcolor import colored
from sumolib import checkBinary

netgenBinary = checkBinary('netgenerate')


def main(configFilePath):
    """Use the network configuration file to generate the network file."""

    print(colored(">> Generating network...", "yellow"))
    runPythonFile([
        netgenBinary,
        '-c', configFilePath],
        "Created network file.")
