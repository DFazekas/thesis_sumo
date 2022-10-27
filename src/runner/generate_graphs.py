import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def percentile(n):
    def percentile_(x):
        return x.quantile(n)
    percentile_.__name__ = 'percentile_{:2.0f}'.format(n * 100)
    return percentile_


def bargraph(data, y, yLabel, outputFile):
    plt.clf()
    graph = sns.barplot(data=data, x="Demand",
                        y=y, hue="Penetration", palette="Paired_r", estimator=np.median, capsize=0.05, errwidth=0.7)
    graph.set_xlabel('Demand (veh/hr)')
    graph.set_ylabel(yLabel)
    legend = graph.legend(title="PR (%)", bbox_to_anchor=(
        1, 1), loc='upper left')
    graph.set_title(f"{y.capitalize()} vs. Demand")
    plt.tight_layout()
    plt.savefig(outputFile, bbox_extra_artists=(legend))


def boxplot(data, y, yLabel, outputFile):
    plt.clf()
    graph = sns.boxplot(data=data, x="Demand",
                        y=y, hue="Penetration", palette="Paired_r")
    graph.set_xlabel('Demand [veh/hr]')
    graph.set_ylabel(yLabel)
    legend = graph.legend(title="PR [%]", bbox_to_anchor=(
        1, 1), loc='upper left')
    graph.set_title(f"{y.capitalize()} vs. Demand")
    plt.tight_layout()
    plt.savefig(outputFile, bbox_extra_artists=(legend))


def main(caseStudyDir):
    outputDir = f"src/{caseStudyDir}/output"
    data = pd.read_csv(f"{outputDir}/alldata.csv")

    tableOutput = f"{outputDir}/tables/table_"
    createTable(data, "Duration", f"{tableOutput}duration.csv")
    createTable(data, "Waiting Time", f"{tableOutput}waitingtime.csv")
    createTable(data, "Time Loss", f"{tableOutput}timeloss.csv")
    createTable(data, "Average Speed", f"{tableOutput}avgspeed.csv")

    boxplotPath = f"{outputDir}/graphs/boxplot_"
    boxplot(data, 'Duration', 'Duration [s]', f"{boxplotPath}duration.png")
    boxplot(data, 'Waiting Time', 'Waiting Time [s]',
            f"{boxplotPath}waitingtime.png")
    boxplot(data, 'Time Loss', 'Time Loss [s]',
            f"{boxplotPath}timeloss.png")
    boxplot(data, 'Time Loss', 'Time Loss [s]',
            f"{boxplotPath}timeloss.png")
    boxplot(data, 'Average Speed', 'Average Speed [m/s]',
            f"{boxplotPath}avgspeed.png")

    bargraphPath = f"{outputDir}/graphs/bargraph_"
    bargraph(data, 'Duration', 'Duration (sec)', f"{bargraphPath}duration.png")
    bargraph(data, 'Waiting Time', 'Waiting Time (sec)',
             f"{bargraphPath}waitingtime.png")
    bargraph(data, 'Time Loss', 'Time Loss (sec)',
             f"{bargraphPath}timeloss.png")
    bargraph(data, 'Time Loss', 'Time Loss (sec)',
             f"{bargraphPath}timeloss.png")
    bargraph(data, 'Average Speed', 'Average Speed (m/s)',
             f"{bargraphPath}avgspeed.png")


def createTable(data: pd.DataFrame, col: str, outfile: str):
    df = data[["Demand", "Penetration", "Run", col]
              ].groupby(["Demand", "Penetration"])[col].median()
    df.to_csv(outfile)
