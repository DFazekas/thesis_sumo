from termcolor import colored
from .utils import runPythonFile
from utils import xml_to_df


def main(inputFilePath, outputFilePath):
    """Processes SSM_reports.xml files into conflicts.csv files."""

    print(colored(">> Processing conflicts file...", "yellow"))

    runPythonFile(
        [
            "python", xml_to_df.__file__,
            '--xml', inputFilePath,
            '--cols', 'begin,end,foe,ego,time,type,value',
                      '-o', outputFilePath,
                      # "--verbose", "True"
        ],
        "Conflicts file processed.", True
    )
