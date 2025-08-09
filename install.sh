
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RESET='\033[0m'  

color_print() {
    local color="$1"
    echo -e "${1}${2}${RESET}"
}

color_print $BLUE "Creating virtual environment..."

if ! python3 -m venv .venv ; then
    color_print $RED "Failed to create virtual environment."
    color_print $RED "Possible Issues include:"
    color_print $RED "  > Python not installed"
    color_print $RED "  > venv module not installed."
    exit 1
fi

color_print $GREEN "Created virtual environment."
source .venv/bin/activate

color_print $BLUE "Installing dependancies..."
if ! pip install -r requirements.txt ; then
    color_print $RED "Failed to install dependancies."
fi

color_print $GREEN "Dependancies successfully installed."

color_print $BLUE "Installing Sapphire..."

if ! pip install -e . ; then
    color_print $RED "Failed to install Sapphire."
    exit 1
fi

color_print $GREEN "Sapphire successfully installed."

