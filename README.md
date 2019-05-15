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

* ```export PIPENV_VENV_IN_PROJECT=True```
* ```pipenv install```
* ```yarn install```
* ```./runner.py```

### Development

* ```export PIPENV_VENV_IN_PROJECT=True```
* ```pipenv install```
* ```yarn install --dev```
* ```./runner.py -r```
