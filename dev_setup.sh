#!/bin/bash

# Prerequisite: run "chmod +x setup_dev.sh" to make this file executable

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
rm get-pip.py

# Install dependencies
python3 -m pip install -r requirements.txt

# Install dev tools
python3 -m pip install -r requirements.dev.txt

# Install build tools
python3 -m pip install --upgrade build twine

echo "Development environment setup complete!"