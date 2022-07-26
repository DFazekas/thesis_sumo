import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
from functools import reduce


if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import sumolib  # noqa


def normalize_conflict_types(df):
    CONFLICTS_LIST = {
        1: 'FOLLOWING',
        2: 'FOLLOWING',
        3: 'FOLLOWING',
        5: 'MERGING',
        6: 'MERGING',
        7: 'MERGING',
        8: 'MERGING',
        9: 'CROSSING',
        10: 'CROSSING',
        12: 'CROSSING',
        13: 'CROSSING',
        11: 'CROSSING',
        111: 'COLLISION'
    }
    df['type'] = df['type'].replace(CONFLICTS_LIST)
    return df


def get_data(file, label):
    df = pd.read_csv(file, sep=",", index_col=None)
    df = normalize_conflict_types(df)
    result = pd.DataFrame(df[['type']].copy().value_counts(), columns=[label])
    print(result)
    return result


def generate_heatmap(data):
    graph = sns.heatmap(data, cmap="flare")
    graph.set_title('Frequency of Conflict Types')
    graph.set_xlabel('PR (%)')
    graph.set_ylabel('Type')
    plt.savefig('output/graphs/conflicts.png')


def get_options(args=None):
    optParser = sumolib.options.ArgumentParser(
        description="Generates a heatmap from conflict data.")
    optParser.add_argument("--files", dest="files",
                           help="[Required] Comma-separated list of conflict data files.")
    options = optParser.parse_args(args=args)

    # Files are required.
    if not options.files:
        optParser.print_help()
        sys.exit(1)

    if options.files:
        options.files = options.files.split(',')

    return options


def main(options):
    allData = []

    # Aggregate all file data together.
    for index, file in enumerate(options.files):
        allData.append(get_data(file, f"Experiment {index}"))

    # Reduce aggregated data into mutual columns.
    mergedData = reduce(lambda left, right: pd.merge(
        left, right, on=["type"], how='outer'), allData).fillna(0)

    # Generate the heatmap from the aggregated data.
    generate_heatmap(mergedData)


if __name__ == "__main__":
    main(get_options())
