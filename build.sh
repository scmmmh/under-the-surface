#!/bin/bash

# The local-config file can be used to set deployment-specific environment settings, such as proxies
if [ -f 'local-config' ]
then
    source local-config
fi

# Update the application and install it in an in-project virtualenv
git pull
export PIPENV_VENV_IN_PROJECT=True
pipenv install
yarn install

# Update the static files
pipenv run ./runner.py

# Run any optional server-restart commands
if [ -f 'post-install' ]
then
    ./post-install
fi
