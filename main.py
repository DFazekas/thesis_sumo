#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
from src.utilities import generate_graph_conflict_heatmap as heatmap
from sumolib import checkBinary  # noqa
from src.runner import run_simulation, process_conflicts
from pathlib import Path
import time

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


demands = [200]  # vehicles per hour. [1200, 1500, 1800]
reruns = 1  # The number of times to rerun the same simulation

# FIXME - I don't think the PR is working. Check both 0% and 100%.
# FIXME - Compare thesis with debug code. It runs 5 seconds. Why?
caseStudyDir = "src/case_study_real_world"


def filter(string, substr):
    return [str for str in string if any(sub in str for sub in substr)]


def main(sumoBinary, options):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # Delete all the previous output data.
    if options.nosim == False:
        clearOutputDirectory()

    # Get all penetration vType distribution files.
    path = "src/config/vTypes"
    fileNames = os.listdir(path)
    vTypeFiles = [f'{path}/{name}' for name in fileNames]
    # vTypeFiles = [vTypeFile[0]]

    # Run grid network x100 at 1000 veh/hr and 0% CVs, average the outputs, aggregrate the SSM data. Repeat for 25%, 50%, 75%, and 100% CVs. Repeat for 1500 veh/hr and 2000 veh/hr.
    # Expecting: 15 data files.

    for dIndex, demand in enumerate(demands):
        print(
            f"""> Applying traffic demand ({colored(f'{dIndex+1}', 'magenta')} / {colored(f'{len(demands)}', 'magenta')})...""")

        for vIndex, vTypeFile in enumerate(vTypeFiles):
            print(
                f""">> Applying CV penetration rate ({colored(f'{vIndex+1}', 'cyan')} / {colored(f'{len(vTypeFiles)}', 'cyan')})...""")

            temp = Path(vTypeFile)
            penetrationRatio = temp.stem.replace('.add', '')

            for runNum in list(range(reruns)):
                prefix = f"d{demand}_p{penetrationRatio}_r{runNum}"
                runStats = {"current": runNum, "total": reruns}
                if options.nosim == False:
                    tic = time.perf_counter()
                    # run_simulation.runGrid(
                    #     sumoBinary, vTypeFile, demand, prefix, runNum, runStats)
                    run_simulation.runRealWorld(
                        sumoBinary, vTypeFile, demand, prefix, runNum, runStats)
                    toc = time.perf_counter()
                    print(
                        f"""SUMO took ({colored(f"{toc-tic:0.4f}", "red")}) seconds.""")

            # Get all SSM files
            # ssmPath = "src/case_study_grid/output/ssm"

            ssmPath = f"{caseStudyDir}/output/ssm"
            ssmFiles = filter(os.listdir(ssmPath), [
                              f"d{demand}_p{penetrationRatio}"])
            ssmAbsFiles = [
                f"{ssmPath}/{ssmFile}" for ssmFile in ssmFiles]
            print(
                f"\t>>> Processing ({colored(len(ssmAbsFiles), 'yellow')}) ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) conflict files...")
            process_conflicts.averageConflicts(
                ssmAbsFiles,
                f"{caseStudyDir}/output/stats/ssm_d{demand}_p{penetrationRatio}.csv")

            print(
                f"\t{colored('[✓]', 'green')} SSM ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) processing complete.")

    print("""\n> Generating SSM report file...""")
    ssmStatPath = f"{caseStudyDir}/output/stats"
    ssmReportFile = f"{caseStudyDir}/output/report.csv"
    process_conflicts.generateReport(ssmStatPath, ssmReportFile)
    print(
        f"""\t{colored('[✓]', 'green')} SSM report generation complete.""")

    # Generate SSM heatmap chart.
    print("""\n> Generating SSM heatmap chart...""")

    heatmap.process_file(f"{caseStudyDir}/output/report.csv",
                         f"{caseStudyDir}/output/graphs")
    print(
        f"""\t{colored('[✓]', 'green')} SSM heatmap generation complete.""")


def clearOutputDirectory():
    """Delete all old output data."""
    folders = [f"{caseStudyDir}/output/ssm",
               f"{caseStudyDir}/output/stats",
               f"{caseStudyDir}/output/dump",
               f"{caseStudyDir}/output/fcd"]

    print(f"""> Deleting old data...""")

    for folder in folders:
        for fileName in os.listdir(folder):
            filePath = os.path.join(folder, fileName)
            try:
                if os.path.isfile(filePath):
                    os.unlink(filePath)
            except Exception as e:
                print(colored(f"Failed to delete {filePath}. Reason {e}"))

    print(f"""\t{colored("[✓]", "green")} Old data successfully deleted.""")

    # TODO: Add real-world case study.


def get_options():
    """Define options for this script and interpret the commandline."""

    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of SUMO.")
    optParser.add_option("--nosim", action="store_true",
                         default=False, help="only reprocess old data.")
    options, _ = optParser.parse_args()
    return options


if __name__ == "__main__":
    # Decide whether to run with/without GUI.
    options = get_options()

    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    main(sumoBinary, options)
