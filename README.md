first project on github YIPPEE

Does the following:
- Takes in an expression or equation as an input.
- Parses it into a form that Python can evaluate properly and quickly with regex.
    - Implicit multiplication converted ("2x" -> "2*x")
    - (NOW FULLY WORKING YIPPEE) Power to `pow()` conversion (`x^y` or `x**y` -> `pow(x, y)`)
- If the input has an equals sign, solves for x on one or both sides of an equation.
    - Uses Newton's method and root division to remove zeros after found, up to 10 potential roots.
    - Filters roots for insanity introduced by inaccuracy from dividing floating point numbers.
- Otherwise, simply evaluate the expression.

Features:
- Domain error handling
- Implicit multiplication management
- All `math` and `cmath` functions (except `log10` and `atan2`)
- Complex numbers (through `cmath` or other valid generations in Python, if needed)
- Very strong chances of solution(s) that are accurate
- Multiple solutions (if relevant) given with self-checking

Requirements: 
- External library `regex` (python's built-in `re` doesn't work because of need for recursion, can be installed if you have Python through running the terminal command: `python -m pip install regex`).

Allows support for both `math` and `cmath` functions, with `math` in class space, and `cmath` as named `c` outside of class space since it overlaps with `math`.

Uses print debugs so you can see inputs/outputs at every step.