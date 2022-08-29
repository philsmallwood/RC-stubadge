#!/bin/bash
### Main Script - Updater ###
### Wrapper script to call python script in
### the correct Virtual Environment
# Switch to VirtualEnv
source /updater/stubadge_env/bin/activate stubadge_env
# Call updater python script
python3 /updater/stubadge_ldap_updater.py
