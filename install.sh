#! /bin/bash

if ! command -v python3.10 &> /dev/null
then
    if command -v apt-get &> /dev/null
    then
        sudo apt-get install python3.10
    elif command -v brew &> /dev/null
    then
        brew install python@3.10
    elif command -v dnf &> /dev/null
    then
        sudo dnf install python3.10 libxcrypt-compat
    elif command -v pacman &> /dev/null
    then
        sudo pacman -S python3.10
    elif command -v zypper &> /dev/null
    then
        sudo zypper install python3.10
    else
        echo "Python 3.10 not found. Please install Python 3.10"
        exit
    fi
fi

# https://isaac-sim.github.io/IsaacLab/main/source/setup/installation/pip_installation.html#installing-isaac-sim

python3.10 -m venv env_isaaclab
source env_isaaclab/bin/activate
pip install -e .
pip install isaaclab[isaacsim,all]==2.0.2 --extra-index-url https://pypi.nvidia.com
