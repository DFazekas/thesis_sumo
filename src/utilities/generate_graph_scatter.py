import seaborn as sns
import matplotlib.pyplot as plt


def main(data, x, y, col, xLabel, yLabel, title, outputFilepath):
    plt.clf()
    graph = sns.lmplot(data=data, x=x, y=y, col=col, hue=col)
    graph.set_axis_labels(xLabel, yLabel)
    # plt.show()
    plt.savefig(outputFilepath)
