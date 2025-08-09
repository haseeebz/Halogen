import subprocess, platform, os, venv, shutil
from pathlib import Path


RED   = '\033[0;31m'
GREEN = '\033[0;32m'
BLUE  = '\033[0;34m'
YELLOW = '\033[33m'
RESET = '\033[0m'  


def color_print(color: str, string: str):
    print(f"{color}{string}{RESET}")


def ask_user(msg: str, options: list[str]) -> str:

    while True:
        choice = input(f"{msg} {options} : ")

        if choice not in options:
            color_print(RED, "Incorrect option!")
            continue

        break


def shell(cmd: str) -> bool:
    output = subprocess.run(
        cmd,
        shell = True
    )

    if output.returncode == 0:
        return True 

    return False



OS = platform.system().lower()

SAPPHIRE_DIR = Path(__file__).resolve().parent
WORKING_DIR = Path(os.getcwd())

VENV_DIR = Path(SAPPHIRE_DIR) / ".venv"


color_print(GREEN, f"Detected OS : {OS}")
color_print(BLUE, "Proceeding with installation...")



if SAPPHIRE_DIR != WORKING_DIR:
    color_print(RED, "Current working directory is not the same directory with 'install.py'. Please change working directory.")
    exit(1)


# Creating the venv

color_print(BLUE, "Creating virtual environment...")

try:
    venv.EnvBuilder(with_pip = True).create(VENV_DIR)
except shutil.SameFileError:
    color_print(YELLOW, f"Virtual environment at {VENV_DIR} already exists? Using this one.")


color_print(GREEN, f"Virtual environment created at {VENV_DIR}")



# installing dependancies

pip_path = VENV_DIR / "bin" / "pip3"


color_print(BLUE, "Installing dependancies...")
success = shell(f"{pip_path} install -r requirements.txt")

if not success:
    color_print(RED, "Failed to install dependancies.")
    exit(1)

color_print(GREEN, "Dependancies installed.")



# Installing sapphire

color_print(BLUE, "Installing Sapphire in virtual env...")
success = shell(f"{pip_path} install -e .")

if not success:
    color_print(RED, "Could not install Sapphire!")
    exit(1)

color_print(GREEN, "Sapphire installed.")
