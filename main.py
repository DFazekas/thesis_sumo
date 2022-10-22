#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
from src.utilities import generate_graph_conflict_heatmap as heatmap
from src.utilities import generate_graph_scatter as scatterGraph
from sumolib import checkBinary  # noqa
from src.runner import process_FCDs, process_tripinfo, run_simulation, process_conflicts
from pathlib import Path
import time
import pandas as pd

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

# FIXME - There only seems to be ~230 cars on the network at any moment.
# FIXME - EV doesn't always drive on incoming traffic. Lower its safety checks.
demands = [2000]  # vehicles per hour. [1200, 1500, 1800]
reruns = 4  # The number of times to rerun the same simulation

# FIXME - I don't think the PR is working. Check both 0% and 100%.
# FIXME - Compare thesis with debug code. It runs 5 seconds. Why?
caseStudyDir = "src/case_study_real_world"


def filter(string, substr):
    return [str for str in string if any(sub in str for sub in substr)]


def averageConflicts(demand, penetrationRatio):
    ssmPath = f"{caseStudyDir}/output/ssm"
    ssmFiles = filter(os.listdir(ssmPath), [
        f"ssm_d{demand}_p{penetrationRatio}"])
    ssmAbsFiles = [
        f"{ssmPath}/{ssmFile}" for ssmFile in ssmFiles]
    print(
        f"\t>>> Processing ({colored(len(ssmAbsFiles), 'yellow')}) ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) conflict files...")
    process_conflicts.averageConflicts(
        ssmAbsFiles,
        f"{caseStudyDir}/output/stats/ssm_d{demand}_p{penetrationRatio}.csv")

    print(
        f"\t{colored('[✓]', 'green')} SSM ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) processing complete.")


def averageTripinfo(demand, penetrationRatio):
    dataDir = f"{caseStudyDir}/output/dump"
    fileNames = filter(os.listdir(dataDir), [
        f"info_d{demand}_p{penetrationRatio}"])
    files = [
        f"{dataDir}/{fileName}" for fileName in fileNames]
    print(
        f"\t>>> Processing ({colored(len(fileNames), 'yellow')}) ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) tripinfo files...")
    process_tripinfo.averageResults(
        files, f"{caseStudyDir}/output/stats/tripinfo_d{demand}_p{penetrationRatio}.csv")
    print(
        f"\t{colored('[✓]', 'green')} Tripinfo ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) processing complete.")


def averageFCDs(demand, penetrationRatio):
    dataDir = f"{caseStudyDir}/output/fcd"
    fileNames = filter(os.listdir(dataDir), [
        f"fcd_d{demand}_p{penetrationRatio}"])
    files = [
        f"{dataDir}/{fileName}" for fileName in fileNames]
    process_FCDs.averageResults(
        files, f"{caseStudyDir}/output/stats/fcd_d{demand}_p{penetrationRatio}.csv")
    print(
        f"\t>>> Processing ({colored(len(fileNames), 'yellow')}) ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) FCD files...")

    print(
        f"\t{colored('[✓]', 'green')} FCD ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) processing complete.")


def generateConflictReport():
    print("""\n> Generating SSM report file...""")
    ssmStatPath = f"{caseStudyDir}/output/stats"
    fileNames = filter(os.listdir(ssmStatPath), [
        f"ssm"])
    files = [
        f"{ssmStatPath}/{fileName}" for fileName in fileNames]
    ssmReportFile = f"{caseStudyDir}/output/report.csv"
    process_conflicts.generateReport(files, ssmReportFile)
    print(
        f"""\t{colored('[✓]', 'green')} SSM report generation complete.""")


def generateTripinfoReport():
    print("""\n> Generating Tripinfo report file...""")
    dir = f"{caseStudyDir}/output/stats"
    fileNames = filter(os.listdir(dir), [
        f"tripinfo_"])
    files = [
        f"{dir}/{fileName}" for fileName in fileNames]
    outputFileName = f"{caseStudyDir}/output/tripinfo_report.csv"
    process_tripinfo.generateReport(files, outputFileName)
    print(
        f"""\t{colored('[✓]', 'green')} Tripinfo report generation complete.""")


def generateFCDReport():
    print("""\n> Generating FCD report file...""")
    dir = f"{caseStudyDir}/output/stats"
    fileNames = filter(os.listdir(dir), [
        f"fcd_"])
    files = [
        f"{dir}/{fileName}" for fileName in fileNames]
    outputFileName = f"{caseStudyDir}/output/fcd_report.csv"
    process_tripinfo.generateReport(files, outputFileName)
    print(
        f"""\t{colored('[✓]', 'green')} FCD report generation complete.""")


def main(sumoBinary, options):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # Delete all the previous output data.
    if options.nosim == False:
        clearOutputDirectory()

    # Get all penetration vType distribution files.
    path = "src/config/vTypes"
    fileNames = os.listdir(path)
    vTypeFiles = [f'{path}/{name}' for name in fileNames]
    # vTypeFiles = ["src/config/vTypes/100_0.add.xml"]

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

            # Average the SSM results for each rerun.
            averageConflicts(demand, penetrationRatio)

            # Average the tripinfo results for each rerun.
            averageTripinfo(demand, penetrationRatio)

            # Average the FCD results for each rerun.
            averageFCDs(demand, penetrationRatio)

    # Aggregate statistics into single report.
    # generateConflictReport()
    generateTripinfoReport()
    generateFCDReport()

    # Generate SSM heatmap chart.
    print("""\n> Generating SSM heatmap chart...""")
    heatmap.process_file(f"{caseStudyDir}/output/report.csv",
                         f"{caseStudyDir}/output/graphs")
    print(
        f"""\t{colored('[✓]', 'green')} SSM heatmap generation complete.""")

    # TODO: Generate graphs based on Tripinfo.
    tripinfoData = pd.read_csv(
        "src/case_study_real_world/output/tripinfo_report.csv", index_col=False)
    scatterGraph.main(data=tripinfoData,
                      x='Penetration (%)', col='Demand (veh/hr)',
                      y='Duration',
                      title='Penetration Vs. Duration at Varying Demands',
                      xLabel='PR (%)', yLabel='Duration (sec)',
                      outputFilepath='src\case_study_real_world\output\graphs/trip_bar.png')


def clearOutputDirectory():
    """Delete all old output data."""
    folders = [f"{caseStudyDir}/output/ssm",
               f"{caseStudyDir}/output/stats",
               f"{caseStudyDir}/output/dump",
               f"{caseStudyDir}/output/fcd",
               f"{caseStudyDir}/output/graphs"]

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
