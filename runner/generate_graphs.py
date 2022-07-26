from termcolor import colored
from .utils import runPythonFile
from output.utils import generate_graph_conflict_heatmap

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


def main():
    """Generate graphs."""

    print(colored(">> Generating heatmap...", "yellow"))

    files = [
        "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\output\\data\\conflicts_2022_07_25-18_21_54.csv",
        "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\output\\data\\conflicts_2022_07_25-18_34_13.csv",
        "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\output\\data\\conflicts_2022_07_25-19_05_01.csv",
        "C:\\Users\\thoma\\OneDrive\\Documents\\Thesis\\drafts\\thesis_sumo\\output\\data\\conflicts_2022_07_25-19_06_32.csv"
    ]

    res = runPythonFile([
        "python", generate_graph_conflict_heatmap.__file__,
        "--files", ",".join(files)
    ], "Heatmap generated.")

    if res:
        print(res)
