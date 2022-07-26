from termcolor import colored
from .utils import runPythonFile
from output.utils import xml_to_df


def main():
    """Processes SSM_reports.xml files into conflicts.csv files."""

    print(colored(">> Processing conflicts file...", "yellow"))
    # xml_to_df.main(xml_to_df.get_options([
    #     '--xml', 'output/data/ssm_reports.xml',
    #     '--cols', 'begin,end,foe,ego,time,type,value',
    #     '-o', 'output/data/conflicts.csv']))

    res = runPythonFile(
        [
            "python", xml_to_df.__file__,
            '--xml', 'output/data/ssm_reports.xml',
            '--cols', 'begin,end,foe,ego,time,type,value',
            '-o', 'output/data/conflicts.csv',
            # "--verbose", "True"
        ],
        "Conflicts file processed.")
    if (res):
        print(res)
