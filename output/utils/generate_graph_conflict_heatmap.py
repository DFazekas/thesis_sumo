import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
import sys
from termcolor import colored
import os
from functools import reduce


if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))
import sumolib  # noqa

def get_data(file, label):
  df = pd.read_csv(file, sep=",", index_col=None)
  result = pd.DataFrame(df[['type']].copy().value_counts(), columns=[label])
  print(result.columns)
  return result


def generate_heatmap(data):
  graph = sns.heatmap(data, cmap="flare")
  graph.set_title('Frequency of Conflict Types')
  graph.set_xlabel('PR (%)')
  graph.set_ylabel('Type')
  plt.savefig('output/graphs/conflicts.png')

def get_options(args=None):
  optParser = sumolib.options.ArgumentParser(description="Generates a heatmap from conflict data.")
  optParser.add_argument("--files", dest="files", help="[Required] Comma-separated list of conflict data files.")
  options = optParser.parse_args(args=args)

  # Column names are required.
  if not options.files:
    optParser.print_help()
    sys.exit(1)

  if options.files:
    options.files = options.files.split(',')

  return options

def main(options):
  allData = []
  
  for index, file in enumerate(options.files):
    allData.append(get_data(file, f"Experiment {index}"))
  
  mergedData = reduce(lambda left,right: pd.merge(left, right, on=["type"], how='outer'), allData).fillna(0)
  generate_heatmap(mergedData)

if __name__ == "__main__":
  main(get_options())