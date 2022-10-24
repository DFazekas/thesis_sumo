import seaborn as sns
import matplotlib.pyplot as plt


def main(data, x, y, hue, xLabel, yLabel, outputFilepath, legendTitle=""):
    plt.clf()
    graph = sns.catplot(data=data, kind='bar', x=x,
                        y=y, hue=hue)
    graph.set_axis_labels(xLabel, yLabel)
    graph.legend.set_title(legendTitle)
    # plt.show()
    plt.savefig(outputFilepath)
