from .utils import runPythonFile
from ..utilities import xml_to_csv
from functools import reduce
import pandas as pd
import numpy as np
import os
import re

CONFLICTS_LIST = {
    '1': 'FOLLOWING',
    '2': 'FOLLOWING',
    '3': 'FOLLOWING',
    '5': 'MERGING',
    '6': 'MERGING',
    '7': 'MERGING',
    '8': 'MERGING',
    '9': 'CROSSING',
    '10': 'CROSSING',
    '12': 'CROSSING',
    '13': 'CROSSING',
    '11': 'CROSSING',
    '111': 'COLLISION'
}


def main(inputFilePath, outputFilePath):
    """Processes SSM_reports.xml files into conflicts.csv files."""

    runPythonFile(
        [
            "python", xml_to_csv.__file__,
            '--xml', inputFilePath,
            '--cols', 'time,type',
            '-o', outputFilePath
        ],
        "Conflicts file processed.", True
    )


def averageConflicts(files, outputFile):
    desiredCols = ['CROSSING', 'FOLLOWING', 'MERGING']
    cols = ['type']
    # Flatten. Average. Export as CSV.
    runData = []
    for file in files:
        data = xml_to_csv.parse_XML(file, cols)
        data['type'] = data['type'].replace(CONFLICTS_LIST)
        data = data.groupby(['type'], as_index=False).size()
        runData.append(data)

    # Merge and average all dataframes by 'type' column.
    df = pd.concat(runData).replace(
        0, np.nan).groupby("type", as_index=False).median()

    # Add missing 'type' rows with value of zero.
    for col in desiredCols:
        if (df['type'].eq(col)).any() == False:
            tempDf = pd.DataFrame({'type': [col], 'size': [0]})
            df = pd.concat((df, tempDf), axis=0)

    # Output as CSV.
    df.to_csv(outputFile, sep=',', index=False)


def generateReport(files: list[str], outputFile: str) -> None:
    """Merges, cleans, and formats all SSM stat files. Exports as CSV.

    Args:
        inputFileDir (str): The directory of the SSM stat files.
        outputFile (str): The directory for the output file.
    """
    dfs = []
    for file in files:
        # Extract the values for demand and PR from the file name.
        demandVal = (re.search('d(\d{2,5})', file)).group(1)
        penVal = (re.search('p(\d{1,3})', file)).group(1)

        # Extract CSV data.
        df = pd.read_csv(file)

        # Remove "collision" conflict type.
        df = df[df["type"].str.contains("COLLISION") == False]

        # Rename columns.
        df = df.rename(columns={'type': 'Type', 'size': 'Occurrence'})

        # Add traffic demand and PR columns.
        df['Demand (veh/hr)'] = demandVal
        df['Penetration (%)'] = penVal

        # Reorder columns.
        df = df[['Penetration (%)', 'Demand (veh/hr)', 'Type', 'Occurrence']]

        dfs.append(df)

    # Merge all the dataframes.
    dfMerged = pd.concat(dfs)

    # Pivot conflict types into columns.
    dfMerged = dfMerged.pivot_table(values='Occurrence', index=[
                                    'Penetration (%)', 'Demand (veh/hr)'], columns='Type')
    dfMerged.reset_index(inplace=True)
    dfMerged.columns.name = None

    # Export as CSV file.
    dfMerged.to_csv(outputFile, index=False)
