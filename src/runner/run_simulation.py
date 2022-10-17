#!/usr/bin/env python3

from termcolor import colored
from ..models.Simulation import Simulation


def main(sumoBinary, networkFilePath: str, vTypeFilePath: str, tripFilePath: str, outputDir: str, demand: float, prefix: str, runNum: int, evTrip):
    # FIXME - This function is basically useless. Tailor it for both case studies.

    sim = Simulation(evTrip)
    sim.run(
        sumoBinary=sumoBinary,
        networkFilePath=networkFilePath,
        vTypeFilePath=vTypeFilePath,
        tripFilePath=tripFilePath,
        outputDir=outputDir,
        demand=demand,
        runNum=runNum,
        prefix=prefix)


def runGrid(sumoBinary, vTypeFile: str, demand: float, prefix: str, runNum: int, runStats):
    gridNetwork = "src/case_study_grid/config/grid.net.xml"
    gridTrips = "src/case_study_grid/config/trips.trips.xml"
    gridOutput = "src/case_study_grid/output"
    evTrip = {"origin": "top1B3", "dest": "D0bottom3"}

    main(sumoBinary=sumoBinary,
         networkFilePath=gridNetwork,
         vTypeFilePath=vTypeFile,
         tripFilePath=gridTrips,
         outputDir=gridOutput,
         demand=demand,
         prefix=prefix,
         evTrip=evTrip,
         runNum=runNum)

    print(
        f"""\t{colored('[✓]', 'green')} Simulation ({colored(runStats['current']+1, 'yellow')} / {colored(runStats['total'],'yellow')}) complete.""")


def runRealWorld(sumoBinary, vTypeFile, demand, runNum):
    realNetwork = "src/case_study_grid/config/grid.net.xml"
    realTrips = "src/case_study_grid/config/trips.trips.xml"
    realOutput = "src/case_study_grid/output"
    evTrip = {"origin": "top1B3", "dest": "D0bottom3"}

    main(sumoBinary,
         realNetwork,
         vTypeFile,
         realTrips,
         realOutput,
         demand,
         runNum,
         evTrip)
