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
    network = "src/case_study_grid/config/grid.net.xml"
    trips = "src/case_study_grid/config/trips.trips.xml"
    output = "src/case_study_grid/output"
    evTrip = {"origin": "top0A2", "dest": "C0bottom2"}

    main(sumoBinary=sumoBinary,
         networkFilePath=network,
         vTypeFilePath=vTypeFile,
         tripFilePath=trips,
         outputDir=output,
         demand=demand,
         prefix=prefix,
         evTrip=evTrip,
         runNum=runNum)

    print(
        f"""\t{colored('[✓]', 'green')} Simulation ({colored(runStats['current']+1, 'yellow')} / {colored(runStats['total'],'yellow')}) complete.""")


def runRealWorld(sumoBinary, vTypeFile: str, demand: float, prefix: str, runNum: int, runStats):
    network = "src/case_study_real_world/config/realworld.net.xml"
    trips = "src/case_study_real_world/config/trips.trips.xml"
    output = "src/case_study_real_world/output"
    evTrip = {"origin": "-256520229#0", "dest": "166612561#0"}

    main(sumoBinary=sumoBinary,
         networkFilePath=network,
         vTypeFilePath=vTypeFile,
         tripFilePath=trips,
         outputDir=output,
         demand=demand,
         prefix=prefix,
         evTrip=evTrip,
         runNum=runNum)

    print(
        f"""\t{colored('[✓]', 'green')} Simulation ({colored(runStats['current']+1, 'yellow')} / {colored(runStats['total'],'yellow')}) complete.""")
