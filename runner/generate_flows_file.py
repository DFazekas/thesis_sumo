from .utils import runPythonFile
from termcolor import colored
import randomTrips


def main(configFilePath):
    """Use the flows configuration file to generate the flows file."""

    print(colored(">> Generating flow file...", "yellow"))
    runPythonFile([
        "python", randomTrips.__file__,
        "-c", configFilePath],
        "Created flow file.")
