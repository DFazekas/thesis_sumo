#!/usr/bin/env python3

from datetime import datetime
import pandas as pd
import xml.etree.ElementTree as et
import os
import sys
from termcolor import colored
from pathlib import Path

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import sumolib  # noqa

data = []
verbose = False
timestamped = True


def get_options(args=None):
    optParser = sumolib.options.ArgumentParser(
        description="Convert an XML file into a Pandas dataframe.")
    optParser.add_argument("--cols", dest="colNames",
                           help="[Required] Comma-separated list of column names, in order (left to right).")
    optParser.add_argument("--xml", dest="xmlFile",
                           help="[Required] Define the XML file.")
    optParser.add_argument("-o", "--output-file", dest="outputFile",
                           default="output/data/df.csv", help="Define the output filepath.")
    optParser.add_argument("--verbose", dest="verbose",
                           type=bool, default=False, help="Verbose logging.")
    optParser.add_argument("--timestamp", dest="timestamp", type=bool, default=False,
                           help="Appends the current time to the end of the output file name.")
    options = optParser.parse_args(args=args)

    # Column names are required.
    if not options.colNames or not options.xmlFile:
        optParser.print_help()
        sys.exit(1)

    if options.colNames:
        options.colNames = options.colNames.split(',')

    if options.verbose is True:
        global verbose
        verbose = True

    if options.timestamp is False:
        global timestamped
        timestamped = False

    return options


def parse(row, node, cols):
    # For each column, check if the node contains an attribute with the same name.
    # If it does, save the attribute's value.
    # If it does not, but the node has children, repeat the search onto the child node.
    # Otherwise, save None and stop.
    log(f"row ({row}) | node ({node}) | cols ({cols})")
    for index, col in enumerate(cols):
        if node.attrib.get(col) is not None:
            log(
                f"\t\tAttr ({colored(col, 'green')}) found. Value ({colored(node.attrib.get(col), attrs=['bold'])})")
            row.append(node.attrib.get(col))
        elif len(list(node)) > 0:
            log(f"\t\tAttr ({colored(col, 'yellow')}) not found. Children found: ({colored(len(list(node)), 'yellow')}).")
            row + parse(row, list(node)[0], cols[index:])
            return row
        else:
            log(f"\t\tAttr ({colored(col, 'red')}) not found nor any children.")
            row.append(None)
            return row
    return row


def parse_XML(xmlFilePath, colNames):
    xtree = et.parse(xmlFilePath)
    xroot = xtree.getroot()
    allRows = []

    for node in xroot:
        log(f"node ({node})")
        row = []
        result = parse(row, node, colNames)
        log(colored(f"\tResult: ({result})", "cyan"))
        allRows.append(result)

    out_df = pd.DataFrame(allRows, columns=colNames)
    return out_df


def log(msg):
    if verbose == True:
        print(msg)


def returnCSV(data: pd.DataFrame) -> str:
    return data.to_csv(sep=',', index=False)


def exportToFile(filepath, data):

    timestamp = ""
    if (timestamped == True):
        timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

    path = Path(filepath)
    newFilePath = "{0}{1}{2}".format(
        Path.joinpath(
            path.parent, path.stem
        ),
        ("_" + timestamp if timestamp != "" else ""),
        path.suffix
    )

    data.to_csv(newFilePath, sep=",", index=False)


def main(options):
    df = parse_XML(options.xmlFile, options.colNames)
    print(df)
    exportToFile(options.outputFile, df)


if __name__ == "__main__":
    main(get_options())
