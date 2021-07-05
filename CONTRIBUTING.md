# Contributing to this Repository 

Thanks for considering contributing to workoutizer. All sorts of contributions are welcome!


## Setup local Development Environment

For local development I recommend to run the development docker container. First clone the repo
```
git clone git@github.com:fgebhart/workoutizer.git
cd workoutizer
```
and start the workoutizer container using the convenience script:
```
./run_docker.sh
```
It might take a while to build the image, run the container and initialize workoutizer. Once up and running, run the
tests with
```
pytest tests/ -n4
```
Once this was successful you are good to go.

In order to run workoutizer use the `wkz` cli. If not done yet, run `wkz init` (optionally with `--demo`):
```
wkz run
```
In case you encounter any issues in the setup process, please open an [issue](https://github.com/fgebhart/workoutizer/issues).


### VS-Code

If you are using VS-Code I suggest to open this repo in a remote container directly using the
[Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).


## Pre-commit Hooks

Several style checking tools (e.g. `black`, `flake8`, `isort`) are configured to run prior to each commit to ensure a
consistent coding style. It is also possible to manually trigger the hook
```
pre-commit run
```
Using the pre-commit hooks is recommended, because the ci pipeline will also check if your changes comply with the
configured style and fail if not.
If you are developing from within a docker container (preferred way), you might want to manually activate the pre-commit 
hooks with
```
pre-commit install
```
in order to apply the checks prior to committing.


## Commit Messages

Please follow these steps when committing to the repo:
* Find a meaningful commit message.
* If your commit addresses a particular issue either include the issue into the commit message or link the issue
  to the PR via the gui.
* Chose one of the following prefixes to label your commit:
   - `ENH`: Enhancement, new functionality
   - `BUG` or `FIX`: Bug fix
   - `DOC`: Additions/updates to documentation
   - `TST`: Additions/updates to tests
   - `BLD`: Updates to the build process/scripts
   - `TYP`: Type annotations
   - `CLN`: Code cleanup
   - `DEP`: Upgrading dependencies
   - `DEV`: Enhancements to the development environment
   - `RFC`: Refactoring
   - `CI`: Github Actions CI pipeline


## Changelog

Whenever a change modifies the behavior of workoutizer from the user perspective, it should be noted in the 
[Changelog](https://github.com/fgebhart/workoutizer/blob/main/CHANGELOG.md). The Changelog is based on
[Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and organizes all source code changes in the following sections:
`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` or `Security`.


----------------------------

In case I did not cover everything, feel free to open an [issue](https://github.com/fgebhart/workoutizer/issues), start
a [discussion](https://github.com/fgebhart/workoutizer/discussions) or find another way to get in touch :)
