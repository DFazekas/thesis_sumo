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


def generate_heatmap(data: pd.DataFrame, outputFile: str, labels):
    plt.clf()
    graph = sns.heatmap(data, cmap="flare", annot=True)
    graph.set_title(labels["title"])
    graph.set_xlabel(labels["xLabel"])
    graph.set_ylabel(labels["yLabel"])
    plt.savefig(outputFile)


def get_options(args=None):
    optParser = sumolib.options.ArgumentParser(
        description="Generates a heatmap from conflict data.")
    optParser.add_argument("--files", dest="files",
                           help="[Required] Comma-separated list of conflict data files.")
    optParser.add_argument("-o", "--output", dest="output",
                           default="graphs/heatmap.png", help="define the output graph filename.")
    options = optParser.parse_args(args=args)

    # Files are required.
    if not options.files:
        optParser.print_help()
        sys.exit(1)

    if options.files:
        options.files = options.files.split(',')

    return options


def process_file(filePath: str, outputDir: str) -> None:
    df = pd.read_csv(filePath, sep=",", index_col=None)

    xLabel = "Demand (veh/hr)"
    yLabel = "CV Penetration (%)"

    matrix_following = df.pivot(
        "Penetration (%)", "Demand (veh/hr)", "FOLLOWING")
    generate_heatmap(
        matrix_following,
        f"{outputDir}/heatmap_following.png",
        {"title": "Frequency of Following Conflicts", "xLabel": xLabel, "yLabel": yLabel})

    matrix_merging = df.pivot("Penetration (%)", "Demand (veh/hr)", "MERGING")
    generate_heatmap(
        matrix_merging,
        f"{outputDir}/heatmap_merging.png",
        {"title": "Frequency of Merging Conflicts", "xLabel": xLabel, "yLabel": yLabel})

    matrix_crossing = df.pivot(
        "Penetration (%)", "Demand (veh/hr)", "CROSSING")
    generate_heatmap(
        matrix_crossing,
        f"{outputDir}/heatmap_crossing.png",
        {"title": "Frequency of Crossing Conflicts", "xLabel": xLabel, "yLabel": yLabel})


def main(options):
    allData = []

    # Aggregate all file data together.
    for index, file in enumerate(options.files):
        allData.append(get_data(file, f"Experiment {index}"))

    # Reduce aggregated data into mutual columns.
    mergedData = reduce(lambda left, right: pd.merge(
        left, right, on=["type"], how='outer'), allData).fillna(0)

    # Generate the heatmap from the aggregated data.
    generate_heatmap(mergedData, options)


if __name__ == "__main__":
    main(get_options())
