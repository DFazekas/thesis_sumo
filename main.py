#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
from sumolib import checkBinary  # noqa
from src.runner import run_simulation, process_conflicts

# Enables the Windows OS to apply color in their terminal.
os.system('color')

# we need to import python modules from the $SUMO_HOME/tools directory
# If the the environment variable SUMO_HOME is not set, try to locate the python
# modules relative to this script
try:
    tools = os.path.join(os.environ['SUMO_HOME'], "tools")
    sys.path.append(tools)
except ImportError:
    sys.exit(colored("please declare environment variable 'SUMO_HOME'", "red"))


demands = [1000]  # vehicles per hour. [1000, 1500, 2000]
reruns = 2  # The number of times to rerun the same simulation


def filter(string, substr):
    return [str for str in string if any(sub in str for sub in substr)]


def main(sumoBinary):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # Get all penetration vType distribution files.
    path = "src/config/vTypes"
    fileNames = os.listdir(path)
    vTypeFile = [f'{path}/{name}' for name in fileNames]
    vTypeFiles = [vTypeFile[0], vTypeFile[1]]

    # Run grid network x100 at 1000 veh/hr and 0% CVs, average the outputs, aggregrate the SSM data. Repeat for 25%, 50%, 75%, and 100% CVs. Repeat for 1500 veh/hr and 2000 veh/hr.
    # Expecting: 15 data files.

    for dIndex, demand in enumerate(demands):
        print(
            f"""> Applying traffic demand ({colored(f'{dIndex+1}', 'magenta')} / {colored(f'{len(demands)}', 'magenta')})...""")

        for vIndex, vTypeFile in enumerate(vTypeFiles):
            print(
                f""">> Applying CV penetration rate ({colored(f'{vIndex+1}', 'cyan')} / {colored(f'{len(vTypeFiles)}', 'cyan')})...""")

            for runNum in list(range(reruns)):
                prefix = f"d{demand}_p{vIndex}_r{runNum}"
                runStats = {"current": runNum, "total": reruns}
                run_simulation.runGrid(
                    sumoBinary, vTypeFile, demand, prefix, runNum, runStats)

            # Get all SSM files
            ssmPath = "src/case_study_grid/output/ssm"
            ssmFiles = filter(os.listdir(ssmPath), [f"d{demand}_p{vIndex}"])
            ssmAbsFiles = [
                f"{ssmPath}/{ssmFile}" for ssmFile in ssmFiles]
            print(
                f">>> Processing ({colored(len(ssmAbsFiles), 'yellow')}) ({colored(f'd{demand}','magenta')}_{colored(f'p{vIndex}', 'cyan')}) conflict files...")
            process_conflicts.averageConflicts(
                ssmAbsFiles,
                f"src/case_study_grid/output/stats/ssm_d{demand}_p{vIndex}.csv")

            print(
                f"\t{colored('[✓]', 'green')} SSM ({colored(f'd{demand}','magenta')}_{colored(f'p{vIndex}', 'cyan')}) processing complete.")

    # Run real-world network x100 at 1000 veh/hr, average the outputs, aggregrate the SSM data. Repeat for 1500 veh/hr and 2000 veh/hr.
    # TODO: Add real-world case study.

    # TODO: Inject a single EV. Can't use the distribution for the other civilian vehicles.

    # Convert ssm reports from XML format into CSV format.
    # runner.process_conflicts.main(
    #     inputFilePath=f"{dir}/output/data/ssm_reports.xml",
    #     outputFilePath=f"{dir}/output/data/conflicts.csv")

    # Generate graphs from ssm reports (CSV format).
    # TODO: These files won't exist until after runtime.
    # files = [
    #     "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\case_studies\\case_study_01\\scenario_01\\output\\data\\conflicts_2022_08_04-18_21_15.csv",
    #     "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\case_studies\\case_study_01\\scenario_01\\output\\data\\conflicts_2022_08_04-18_29_26.csv",
    #     "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\case_studies\\case_study_01\\scenario_01\\output\\data\\conflicts_2022_08_04-18_29_59.csv"
    # ]
    # runner.generate_graphs.main(
    #     inputFilePaths=files,
    #     outputFilePath=f"{dir}/output/graphs/heatmap.png"
    # )


def get_options():
    """Define options for this script and interpret the commandline."""

    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of SUMO.")
    options, _ = optParser.parse_args()
    return options


if __name__ == "__main__":
    # Decide whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    main(sumoBinary)
