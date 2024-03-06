#!/bin/bash

# Check if Python 3.7 is installed
if ! command -v python3.7 &> /dev/null
then
    echo "Python 3.7 doesn't seem to be installed.  Do you have a weird installation?"
    echo "If you have another python version up to 3.6+, use it to run run.py instead of this script."
    exit 1
fi

# Check if pip is available for the installed Python version
if ! python3.7 -m pip --version &> /dev/null
then
    echo "Pip for Python 3.7 doesn't seem to be installed. Installing it now."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.7
fi

# Upgrade pip and install requirements
python3.7 -m pip install --upgrade pip
python3.7 -m pip install -r requirements.txt

