#!/bin/bash

# Check if Python 3.6 or greater is installed
if ! command -v python3.6 &> /dev/null
then
    echo "Python 3.6 or greater doesn't seem to be installed.  Please install it and try again."
    exit 1
fi

# Check if Python 3.6 can run the script
if ! python3.6 -c "import run_py; print('Script can run')" &> /dev/null
then
    echo "Python 3.6 can't run the script.  Please make sure it's installed and the script is correct."
    exit 1
fi

# Run the script
python3.6 run.py
