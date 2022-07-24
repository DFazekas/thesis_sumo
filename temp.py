from pathlib import Path
from datetime import datetime

timestamp = datetime.now().strftime('%Y_%m_%d-%H_%M_%S')

originalFileName = "output/data/conflicts.csv"
p = Path(originalFileName)
newFileName = "{0}_{1}{2}".format(Path.joinpath(p.parent, p.stem), timestamp, p.suffix)
print(newFileName)