from termcolor import colored
from .utils import runPythonFile
from ..utilities import xml_to_csv


def main(inputFilePath, outputFilePath):
    """Processes SSM_reports.xml files into conflicts.csv files."""

    print(colored(">> Processing conflicts file...", "yellow"))

    runPythonFile(
        [
            "python", xml_to_csv.__file__,
            '--xml', inputFilePath,
            '--cols', 'begin,end,foe,ego,time,type,value',
                      '-o', outputFilePath,
                      # "--verbose", "True"
        ],
        "Conflicts file processed.", True
    )
