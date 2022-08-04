from termcolor import colored
from .utils import runPythonFile
from utils import generate_graph_conflict_heatmap

# def main():
#     """Generate graphs based on the output FCD data."""

#     print(colored(">> Generating graphs...", "yellow"))
#     plot_trajectories.main(plot_trajectories.getOptions(
#         ["output/data/fcd.xml", "-c", "config/graphs/xpos_speed_trajectory.xml"]))
#     plot_trajectories.main(plot_trajectories.getOptions(
#         ["output/data/fcd.xml", "-c", "config/graphs/time_v_xpos_trajectory.xml"]))
#     plot_trajectories.main(plot_trajectories.getOptions(
#         ["output/data/fcd.xml", "-c", "config/graphs/time_v_speed_trajectory.xml"]))

#     print("Graphs generated.\n")


def main(inputFilePaths, outputFilePath):
    """Generate graphs."""

    print(colored(">> Generating heatmap...", "yellow"))

    runPythonFile([
        "python", generate_graph_conflict_heatmap.__file__,
        "--files", ",".join(inputFilePaths),
        "-o", outputFilePath
    ], "Heatmap generated.", True)
