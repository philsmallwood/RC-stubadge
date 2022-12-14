#! /bin/bash
### Bash Script to configure python virtual env for Script ###
# Create VirtualEnv
python3 -m venv stubadge_env
# Switch to VirtualEnv
source ./stubadge_env/bin/activate stubadge_env
# Install required packages
# Self-created packages are included in the 
# installer folder
pip3 install -r requirements.txt
