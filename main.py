#!/usr/bin/env python3

# @file   runner.py
# @author Devon Fazekas
# @date   2022-05-04

import optparse
from termcolor import colored
import os
import sys
from src.utilities import generate_graph_bar, generate_graph_conflict_heatmap as heatmap
from src.utilities import generate_graph_scatter as scatterGraph
from src.utilities import generate_graph_bar as barGraph
from sumolib import checkBinary  # noqa
from src.runner import process_FCDs, process_tripinfo, run_simulation, process_conflicts
from pathlib import Path
import time
import pandas as pd
from typing import Callable

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


demands = [10, 20, 30]  # vehicles per hour. [1200, 1500, 1800]
reruns = 8  # The number of times to rerun the same simulation

caseStudyDir = "src/case_study_real_world"


def filter(string, substr):
    return [str for str in string if any(sub in str for sub in substr)]


def aggregateData(dataDirName: str, title: str, aggregator: Callable):
    dataDir = f"{caseStudyDir}/output/{dataDirName}"
    fileNames = os.listdir(dataDir)
    files = [
        f"{dataDir}/{fileName}" for fileName in fileNames]
    aggregator(
        files, f"{caseStudyDir}/output/agg/{title.lower()}.csv")
    print(
        f"\t{colored('[✓]', 'green')} {title.upper()} aggregation complete.")


def averageData(demand: int, penetrationRatio: str, dirName: str, title: str, averager: Callable):
    # FIXME - make modular. Inject averageResults function.
    dataDir = f"{caseStudyDir}/output/{dirName}"
    fileNames = filter(os.listdir(dataDir), [
        f"{title.lower()}_d{demand}_p{penetrationRatio}"])
    files = [
        f"{dataDir}/{fileName}" for fileName in fileNames]

    outputFile = f"{caseStudyDir}/output/stats/{title.lower()}_d{demand}_p{penetrationRatio}.csv"
    averager(
        files, outputFile)
    print(
        f"\t{colored('[✓]', 'green')} {title.upper()} ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) processing complete.")


def generateReport(inputDirName: str, title: str, reporter: Callable):
    dir = f"{caseStudyDir}/output/{inputDirName}"
    fileNames = filter(os.listdir(dir), [
        f"{title.lower()}"])
    files = [
        f"{dir}/{fileName}" for fileName in fileNames]
    print(f"file count: {len(files)}")
    outputFileName = f"{caseStudyDir}/output/{title.lower()}_report.csv"
    reporter(files, outputFileName)
    print(
        f"""\t{colored('[✓]', 'green')} {title.upper()} report generation complete.""")


def mergeAllData():
    fcdFileName = "src\case_study_real_world\output/agg/fcd.csv"
    tripinfoFileName = "src\case_study_real_world\output/agg/tripinfo.csv"
    ssmFileName = "src\case_study_real_world\output/agg\ssm.csv"

    fcd = pd.read_csv(fcdFileName)
    tripinfo = pd.read_csv(tripinfoFileName)
    ssm = pd.read_csv(ssmFileName)

    tripinfo_fcd = pd.merge(tripinfo, fcd, how='left', left_on=[
        "Demand", "Penetration", "Run"], right_on=["Demand", "Penetration", "Run"])
    all = pd.merge(tripinfo_fcd, ssm, how='left', left_on=[
        "Demand", "Penetration", "Run"], right_on=["Demand", "Penetration", "Run"])

    all = all.sort_values(by=["Demand", "Penetration", "Run"])
    all.to_csv("src\case_study_real_world\output/alldata.csv", index=False)


def main(sumoBinary, options):
    """Generates all prerequisite files to run the simulation, export data, and process the data."""

    # Delete all the previous output data.
    if options.nosim == False:
        clearOutputDirectory()

    totalTic = time.perf_counter()
    print(
        f"\n> Running experiments...")

    # Get all penetration vType distribution files.
    path = "src/config/vTypes"
    fileNames = os.listdir(path)
    vTypeFiles = [f'{path}/{name}' for name in fileNames]
    # vTypeFiles = ["src/config/vTypes/100_0.add.xml"]

    # Run grid network x100 at 1000 veh/hr and 0% CVs, average the outputs, aggregrate the SSM data. Repeat for 25%, 50%, 75%, and 100% CVs. Repeat for 1500 veh/hr and 2000 veh/hr.
    # Expecting: 15 data files.

    for dIndex, demand in enumerate(demands):
        print(
            f"""\t> Applying traffic demand ({colored(f'{dIndex+1}', 'magenta')} / {colored(f'{len(demands)}', 'magenta')})...""")

        for vIndex, vTypeFile in enumerate(vTypeFiles):
            print(
                f"""\t\t> Applying CV penetration rate ({colored(f'{vIndex+1}', 'cyan')} / {colored(f'{len(vTypeFiles)}', 'cyan')})...""")

            temp = Path(vTypeFile)
            penetrationRatio = temp.stem.replace('.add', '')

            for runNum in list(range(reruns)):
                print(
                    f"""\t\t\t> Starting run ({colored(f'{runNum+1}', 'yellow')} / {colored(f'{reruns}', 'yellow')})...""")

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

            # Average the results for each rerun.
            print(
                f"\t\t> Averaging ({colored(f'd{demand}','magenta')}_{colored(f'p{penetrationRatio}', 'cyan')}) files...")
            averageData(demand, penetrationRatio, "ssm", "ssm",
                        process_conflicts.averageResults)
            averageData(demand, penetrationRatio, "dump", "tripinfo",
                        process_tripinfo.averageResults)
            averageData(demand, penetrationRatio, "fcd", "fcd",
                        process_FCDs.averageResults)

    totalToc = time.perf_counter()
    print(
        f"""\n{colored('[✓]', 'green')} All experiments completed in ({colored(f"{totalToc-totalTic:0.4f}", "red")}) seconds.""")

    # Aggregate all data into a single CSV file.
    print(
        f"\n> Aggregating dump files...")
    aggregateData("dump", "tripinfo", process_tripinfo.aggregate)
    aggregateData("ssm", "ssm", process_conflicts.aggregate)
    aggregateData("fcd", "fcd", process_FCDs.aggregate)
    mergeAllData()

    # Aggregate statistics into single report.
    # FIXME - Join FCD with TripInfo.
    print("""\n> Generating report files...""")
    generateReport("stats", "tripinfo",
                   process_tripinfo.generateReport)
    generateReport("stats", "ssm",
                   process_conflicts.generateReport)
    generateReport("stats", "fcd",
                   process_FCDs.generateReport)

    # Generate charts.
    print("""\n> Generating charts...""")
    heatmap.process_file(f"{caseStudyDir}/output/ssm_report.csv",
                         f"{caseStudyDir}/output/graphs")
    print(
        f"""\t{colored('[✓]', 'green')} SSM heatmap generation complete.""")

    # TODO: Generate graphs based on Tripinfo.
    tripinfoData = pd.read_csv(
        "src/case_study_real_world/output/tripinfo_report.csv", index_col=False)
    barGraph.main(data=tripinfoData,
                  x='Demand (veh/hr)', hue='Penetration (%)',
                  y='Duration',
                  xLabel='Demand (veh/hr)', yLabel='Duration (sec)',
                  legendTitle="PR (%)",
                  outputFilepath='src\case_study_real_world\output\graphs/bargraph_duration.png')
    print(
        f"""\t{colored('[✓]', 'green')} Demand Vs. Duration bargraph generated.""")

    barGraph.main(data=tripinfoData,
                  x='Demand (veh/hr)', hue='Penetration (%)',
                  y='Waitingtime',
                  xLabel='Demand (veh/hr)', yLabel='Waitingtime (sec)',
                  legendTitle="PR (%)",
                  outputFilepath='src\case_study_real_world\output\graphs/bargraph_waitingtime.png')
    print(
        f"""\t{colored('[✓]', 'green')} Demand Vs. Waiting Time bargraph generated.""")

    barGraph.main(data=tripinfoData,
                  x='Demand (veh/hr)', hue='Penetration (%)',
                  y='Timeloss',
                  xLabel='Demand (veh/hr)', yLabel='Timeloss (sec)',
                  legendTitle="PR (%)",
                  outputFilepath='src\case_study_real_world\output\graphs/bargraph_timeloss.png')
    print(
        f"""\t{colored('[✓]', 'green')} Demand Vs. Time Loss bargraph generated.""")

    barGraph.main(data=tripinfoData,
                  x='Demand (veh/hr)', hue='Penetration (%)',
                  y='Waitingcount',
                  xLabel='Demand (veh/hr)', yLabel='Waiting Count',
                  legendTitle="PR (%)",
                  outputFilepath='src\case_study_real_world\output\graphs/bargraph_waitingcount.png')
    print(
        f"""\t{colored('[✓]', 'green')} Demand Vs. Waiting Count bargraph generated.""")

    speedData = pd.read_csv(
        "src/case_study_real_world/output/fcd_report.csv", index_col=False)
    barGraph.main(data=speedData,
                  x='Demand (veh/hr)', hue='Penetration (%)',
                  y='Speed',
                  xLabel='Demand (veh/hr)', yLabel='Avg. Speed (m/s)',
                  legendTitle="PR (%)",
                  outputFilepath='src\case_study_real_world\output\graphs/bargraph_avgspeed.png')
    print(
        f"""\t{colored('[✓]', 'green')} Demand Vs. Avg Speed bargraph generated.""")


def clearOutputDirectory():
    """Delete all old output data."""
    folders = [f"{caseStudyDir}/output/ssm",
               f"{caseStudyDir}/output/stats",
               f"{caseStudyDir}/output/dump",
               f"{caseStudyDir}/output/fcd",
               f"{caseStudyDir}/output/graphs",
               f"{caseStudyDir}/output/agg"]

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
