from .utils import runPythonFile
from termcolor import colored
from sumolib import checkBinary

netgenBinary = checkBinary('netgenerate')


def main(configFilePath, options=[]):
    """Use the network configuration file to generate the network file."""

    print(colored(">> Generating network...", "yellow"))
    runPythonFile([
        netgenBinary,
        '-c', configFilePath, *options],
        "Created network file.")
