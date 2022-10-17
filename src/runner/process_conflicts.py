from termcolor import colored
from .utils import runPythonFile
from ..utilities import xml_to_csv
from functools import reduce
import pandas as pd
import numpy as np

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
    print(f"SSM file count: {len(files)}")
    cols = ['type']
    # Flatten. Average. Export as CSV.
    runData = []
    for file in files:
        data = xml_to_csv.parse_XML(file, cols)
        data['type'] = data['type'].replace(CONFLICTS_LIST)
        data = data.groupby(['type'], as_index=False).size()
        runData.append(data)

    print(runData)
    df = pd.concat(runData).replace(
        0, np.nan).groupby("type", as_index=False).mean()

    print(f'df: {df}')

    df.to_csv(outputFile, sep=',', index=False)
