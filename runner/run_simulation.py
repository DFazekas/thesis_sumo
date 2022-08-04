from .utils import runPythonFile
from termcolor import colored

SIM_DURATION = '200'  # In seconds.


def main(sumoBinary, configFilePath):
    """Run Sumo using the configuration file."""

    print(colored(">> Running simulation...", "yellow"))
    runPythonFile([
        sumoBinary,
        '-c', configFilePath,
        '-e', SIM_DURATION
    ], "Simultion over.", True)

# TODO: Ensure graphs still generate.
