from .utils import runPythonFile
from termcolor import colored
import randomTrips


def main(configFilePath, networkFilePath, outputFilePath, options=[]):
    """Use the flows configuration file to generate the flows file."""

    print(colored(">> Generating flow file...", "yellow"))
    runPythonFile(
        [
            "python", randomTrips.__file__,
            "-c", configFilePath,
            "-n", networkFilePath,
            "-o", outputFilePath,
            *options
        ],
        "Created flow file.", True)
