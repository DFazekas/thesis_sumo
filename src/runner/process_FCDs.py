from ..utilities import xml_to_csv
import pandas as pd
import re


def aggregate(files: list[str], outputFile: str):
    runData = []
    cols = ['id', 'speed']
    for file in files:
        # Extract the values for demand and PR from the file name.
        demand = (re.search('d(\d{2,5})', file)).group(1)
        pr = (re.search('p(\d{1,3})', file)).group(1)
        run = (re.search('r(\d{1,3})', file)).group(1)

        data = xml_to_csv.parse_XML(file, cols).dropna()
        df = pd.DataFrame([round(data['speed'].median(), 2)],
                          columns=["Average Speed"])
        df['Demand'] = demand
        df['Penetration'] = pr
        df['Run'] = run
        runData.append(df)

    data = pd.concat(runData)
    data.to_csv(outputFile, sep=',', index=False)


def averageResults(files, outputFile):
    runData = []
    cols = ['id', 'speed']
    for file in files:
        data = xml_to_csv.parse_XML(file, cols).dropna()
        runData.append(data)

    data = pd.concat(runData).groupby('id')[['speed']].agg(
        lambda x: x.astype(float).median())

    data.to_csv(outputFile, sep=',', index=False)


def generateReport(files: list[str], outputFile: str) -> None:
    """Merges, cleans, and formats all FCD stat files. Exports as CSV.

    Args:
        inputFileDir (str): The directory of the stat files.
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
