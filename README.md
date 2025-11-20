# STRIPE-kit

## Install

Due to the unique requirements of Isaac Lab, the recommended way of installing
is to use the [`install.sh`](./install.sh) script. It ensures
`python3.10` is installed, compile requirements are installed, installs
this and Isaac Lab.

## Static Analysis

Isaac Lab is a large codebase, with at least three different ways of installing.
For simplicity, we all have agreed to have the PIP installation in the
environment. The problem with that installation though, is that for static
analysis purposes, the import paths would differ from how they should be for
Isaac Lab to pick them up. For example in order to import something from
`isaaclab` you would have to do `isaaclab.source.isaaclab.isaaclab.scene`
instead of `isaaclab.scene` which is how during runtime things are actually
available. In order to fix this, we have added paths to the
`python.analysis.extraPaths` in the `settings.json` file. This is a
pretty solid solution, but it is not very extensible. So please if your static
analyzer is complaining, add a path fitting for your system to the
`settings.json` file. The idea is to find your environment path, and then
add `lib/python3.10/site-packages/isaaclab/source/isaaclab/` to it.
