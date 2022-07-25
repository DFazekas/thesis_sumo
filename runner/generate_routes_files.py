from .utils import runPythonFile
from termcolor import colored
from sumolib import checkBinary

jtrrouterBinary = checkBinary('jtrrouter')


def main(configFilePath):
    """Use the routes configuration file to generate the routes file."""

    print(colored(">> Generating routes file...", "yellow"))
    runPythonFile([jtrrouterBinary, '-c', configFilePath],
                  "Created routes file.")
