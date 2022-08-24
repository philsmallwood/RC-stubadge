#! /bin/bash
### Main Script - Updater ###
### Wrapper script to call python script in
### the correct Virtual Environment
# Switch to VirtualEnv
source ./stubadge_env/bin/activate stubadge_env
# Call updater python script
python3 stubadge_ldap_updater.py
