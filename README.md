# Solve For X

SfX is a Python program for solving for an unknown variable in an equation input through the command line.

## Features:
- Optional expression evaluation
- Newton's Method for root-finding
- Domain error handling
- Implicit multiplication management
- All `math` and `cmath` functions
- Real and complex numbers
- High accuracy/precision multiple solutions with self-checking

## Requirements: 
- External library `regex` (python's built-in `re` module is insufficient, can be installed if you have Python through running the terminal command: `python -m pip install regex`).

Allows support for both `math` and `cmath` functions, with `math` in class space, and `cmath` as named `c` outside of class space due to overlap with `math`.

Uses print debugs so you can see inputs/outputs at every step.