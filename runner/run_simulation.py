from .utils import runPythonFile
from termcolor import colored

SIM_DURATION = '200'  # In seconds.


def main(sumoBinary, configFilePath):
    """Run Sumo using the configuration file."""

    print(colored(">> Running simulation...", "yellow"))
    res = runPythonFile([
        sumoBinary,
        '-c', configFilePath,
        '-e', SIM_DURATION
    ], "Simultion over.")

    if res:
        print(res)
