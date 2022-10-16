from .utils import runPythonFile
from termcolor import colored
from sumolib import checkBinary

jtrrouterBinary = checkBinary('jtrrouter')


def main(configFilePath, networkFilePath, routesFilePath, vehicleTypeFilePath, outputFilePath, options=[]):
    """Use the routes configuration file to generate the routes file."""

    print(colored(">> Generating routes file...", "yellow"))
    runPythonFile(
        [
            jtrrouterBinary, '-c', configFilePath,
            "-n", networkFilePath,
            "-r", routesFilePath,
            "-a", vehicleTypeFilePath,
            "-o", outputFilePath,
            *options
        ],
        "Created routes file.", True)
