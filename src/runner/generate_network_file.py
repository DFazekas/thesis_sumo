from .utils import runPythonFile
from termcolor import colored
from sumolib import checkBinary

netgenBinary = checkBinary('netgenerate')


def main(configFilePath, outputFilePath, options=[]):
    """Use the network configuration file to generate the network file."""

    print(colored(">> Generating network...", "yellow"))
    runPythonFile(
        [
            netgenBinary,
            '-c', configFilePath,
            '-o', outputFilePath,
            *options
        ],
        "Created network file.", True)
