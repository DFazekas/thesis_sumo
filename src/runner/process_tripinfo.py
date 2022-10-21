from .utils import runPythonFile
from ..utilities import xml_to_csv
from functools import reduce
import pandas as pd
import numpy as np
import os
import re


def averageResults(files, outputFile):
    runData = []
    cols = ['id', 'duration', 'waitingTime', 'stopTime', 'timeLoss']
    for file in files:
        data = xml_to_csv.parse_XML(file, cols)
        df = data[data['id'].str.contains("EV")]
        runData.append(df)

    data = pd.concat(runData).groupby('id')[['duration', 'waitingTime',
                                             'stopTime', 'timeLoss']].agg(lambda x: x.astype(float).mean())
    data.to_csv(outputFile, sep=',', index=False)


def generateReport(files: list[str], outputFile: str) -> None:
    """Merges, cleans, and formats all Tripinfo stat files. Exports as CSV.

    Args:
        inputFileDir (str): The directory of the Tripinfo stat files.
        outputFile (str): The directory for the output file.
    """

    dfs = []
    for file in files:
        # Extract the values for demand and PR from the file name.
        demandVal = (re.search('d(\d{2,5})', file)).group(1)
        penVal = (re.search('p(\d{1,3})', file)).group(1)

        # Extract CSV data.
        df = pd.read_csv(file)

        # Rename columns.
        df.columns = df.columns.str.capitalize()

        # Add traffic demand and PR columns.
        df['Demand (veh/hr)'] = demandVal
        df['Penetration (%)'] = penVal

        dfs.append(df)

    # Merge all the dataframes.
    dfMerged = pd.concat(dfs)

    # # Export as CSV file.
    dfMerged.to_csv(outputFile, index=False)
