from .utils import runPythonFile
from termcolor import colored
import traci
import subprocess
SIM_DURATION = '200'  # In seconds.


def main(sumoBinary, configFilePath, options=[]):
    """Run Sumo using the configuration file."""

    print(colored(">> Running simulation...", "yellow"))
    # runPythonFile([
    #     sumoBinary,
    #     '-c', configFilePath,
    #     '-e', SIM_DURATION,
    #     *options
    # ], "Simulation over.", True)
    try:
        print(options)
        print(subprocess.run(
            [
                sumoBinary,
                '-c', configFilePath,
                # '-e', SIM_DURATION,
                *options
            ]))
    except Exception as err:
        print(err)
    # runSimulation(3600 * 2, sumoBinary, configFilePath, options)


def runSimulation(maxSteps, sumoBinary, configFilePath, options=[]):
    step = 0

    traci.start([
        sumoBinary,
        '-c', configFilePath,
        '-e', SIM_DURATION,
        *options
    ])

    while step < maxSteps:
        step += 1
        print(f'step: {step}')
        traci.simulationStep()

    traci.close()
    print(colored("Simulation complete.", "yellow"))
