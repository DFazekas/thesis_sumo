import subprocess
from termcolor import colored
from datetime import datetime


def runPythonFile(fileExecutable, successStr="", verbose=False):
    """Runs a Python executable as a subprocess.

    Args:
        fileExecutable (str): The executable Python file to run.
        successStr (str, optional): The message to display in the event of a successful execution. Defaults to "".

    Returns:
        str: Any stdout from the executable.
    """
    response = subprocess.run(
        fileExecutable, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if response.returncode == 0:
        msg = f"\t{colored('Success.', 'green')}\n"
        if (successStr):
            msg = f"\t{colored('Success >>', 'green')} {successStr}\n"

        print(msg)

        if verbose:
            log(response)

        return {response}
    else:
        errors = "\n\t".join(response.stderr.split("\n"))
        print(
            f"\t{colored(errors, 'red')}\n")
        raise Exception(errors)


def log(process):
    # Converts all data into strings, removes trailing newlines, and indents newlines.
    data = {
        "args": ", ".join(process.args),
        "returncode": str(process.returncode),
        "stdout": "\n\t".join(process.stdout.split("\n")).rstrip(),
        "stderr": "\n\t".join(process.stderr.split("\n")).rstrip()
    }
    with open('logs.txt', 'a') as f:
        # Print time stamp.
        f.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')

        # Print data.
        for (key, value) in data.items():
            f.write(f"{key}: {value} \n")

        # Print divider.
        f.write(f"\n{'='*10}\n\n")
