import subprocess
from termcolor import colored


def runPythonFile(fileExecutable, successStr=""):
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
        return response.stdout
    else:
        errors = "\n\t".join(response.stderr.split("\n"))
        print(
            f"\t{colored(errors, 'red')}\n")
        raise Exception("")
