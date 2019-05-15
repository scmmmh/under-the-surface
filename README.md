# Under the Surface

The *Under the Surface* project combines a data-set with management scripts for a simple, static digital archive. In
this specific instance, the archive is targeted at surfacing authors, composers, and artists who have sunk under the
canonical surface.

## Dependencies

The following dependencies must be installed as pre-requisites:

* Python 3
* Pipenv
* Yarn

## Running

To run and build the Under the Surface site, use the instructions below, depending on the environment.

### Production

To build in production mode, run the following commands in sequence:

* ```export PIPENV_VENV_IN_PROJECT=True```
* ```pipenv install```
* ```yarn install```
* ```./runner.py```

Alternatively you can run the ```build.sh``` script to fully automatically pull the latest changes, install all
dependencies, and rebuild the site.

### Development

To build in development mode, run the following commands in sequence:

* ```export PIPENV_VENV_IN_PROJECT=True```
* ```pipenv install```
* ```yarn install --dev```
* ```./runner.py -d```

These will start the builders in automatic content re-build mode, automatic styling and javascript re-build mode, and
start a webserver at http://localhost:8080. To terminate the builders, press ```CTRL+C```.
