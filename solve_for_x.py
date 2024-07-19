import regex as re
from math import *
import ast
import math
import cmath as c

pow = __builtins__.pow

# Get all names from math module
math_names = {name for name in dir(math)}
cmath_names = {name for name in dir(c)}

epsilon = 2.220446049250313e-16
sqrtepsilon = 1.4901161193847656e-08 # Square root of Python epsilon

builtins = {"abs", "c"}
# Regex for implicit multiplication can't handle these functions, 
# it thinks it's multiplication because of a number followed by a bracket.
undesired = {"log10", "atan2"}
math_names = math_names.union(builtins).union(cmath_names)#.difference(undesired)

def sgn(x):
    return 1 if x > 0 else -1 if x < 0 else 0

def bracketCheck(expression):
    # Check if brackets are balanced
    stack = []
    bracket_map = {')': '(', '}': '{', ']': '['}
    for c in expression:
        if c in bracket_map.values():
            stack.append(c)
        elif c in bracket_map:
            if not stack or bracket_map[c] != stack.pop():
                return False
    return not stack

def replace_exponentiation(expression):
    # Regex pattern to match the base and exponent of ** operator
    pattern = re.compile(r'(\w*\((?:[^()]++|(?1))*+\)|\b\w+\b|\d+\.\d+|d+)\*\*(-?\w*\((?:[^()]++|(?1))*+\)|-?\b\w+\b|\d+\.\d*|\d+)')
    # Convert ** operator to pow function - seems much faster
    while '**' in expression:
        expression = pattern.sub(r'pow(\1,\2)', expression)
    return expression

def insert_multiplication_signs(equation):
    # Replace terms like "2x" with "2*x"
    equation = re.sub(r'(\d)(x)', r'\1*\2', equation)
    equation = re.sub(r'(x)(\d)', r'\1*\2', equation)
    equation = re.sub(r'(\d)(\()', r'\1*\2', equation)
    equation = re.sub(r'(\))(\d)', r'\1*\2', equation)
    # Replace terms like "2sin(x)" with "2*sin(x)"
    equation = re.sub(r'(\d)([a-ik-zA-Z])', r'\1*\2', equation)
    # Handle cases like (x)(x) and sin(x)x
    equation = re.sub(r'(\))(\()', r'\1*\2', equation)
    equation = re.sub(r'(x)([a-zA-Z])', r'\1*\2', equation)
    equation = re.sub(r'(\))([a-zA-Z])', r'\1*\2', equation)
    # equation = re.sub(r'([a-zA-Z])(\()', r'\1*\2', equation)
    # equation = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', equation)
    return equation

def getInput():
    while True:
        equation = input("\nEnter an equation in terms of x, or an expression without an equals sign or variables:\n").strip().lower().replace(" ","").replace("^","**")
        equation = replace_exponentiation(equation)
        equation = insert_multiplication_signs(equation)
        eq = checkInput(equation)
        if eq is None:
            continue
        out, onlyeval = eq[0].split("="), eq[1]
        out = equation if onlyeval else f"({out[0]})-({out[1]})"
        print(f"\nInterpreted {'expression' if onlyeval else 'equation'}: {out}{'' if onlyeval else ' = 0'}\n")
        # print(out)
        return out, onlyeval

def checkInput(equation):
    onlyeval = False if "=" in equation else True
    if onlyeval:
        if not(bracketCheck(equation)):
            print("Incorrect brackets.")
            return None
        names = set(node.id for node in ast.walk(ast.parse(equation)) if isinstance(node, ast.Name))
        if names - math_names != set():
            print("Invalid variable(s) or function(s).")
            return None
        
    else:
        separate = equation.split("=")
        if len(separate) > 2:
            print("Only one equals sign allowed.")
            return None
            
        if "" in separate:
            print("Empty side of equation.")
            return None

        for part in separate:
            if not bracketCheck(part):
                print("Incorrect brackets.")
                return None
        # print(separate)
        # Extract variable names
        names = set(
            node.id for node in ast.walk(ast.parse(separate[0])) if isinstance(node, ast.Name)
        ).union(
            node.id for node in ast.walk(ast.parse(separate[1])) if isinstance(node, ast.Name)
        )
        
        if names - math_names != {"x"}:
            print("Invalid variable(s) or function(s).")
            return None

    for i in names:
        if i in {"log"}:
            print("Note: using logs can't guarantee precision. or even a solution found.")
        elif i in undesired:
            print(i, "is an unsupported function.")
            return None

    return equation, onlyeval

def applyDivision(equation, foundroot):
    return "(" + equation + ")/(x-(" + str(foundroot)+"))"

def evaluate(expression, x):
    try:
        return eval(expression)
    except:
        return None

def getDerivativeConsts(x):
    h = x * sqrtepsilon if x != 0 else sqrtepsilon
    xph = x + h
    xmh = x - h
    return h, xph, xmh

def firstDerivative(equation, x):
    h, xph, xmh = getDerivativeConsts(x)
    fxph = evaluate(equation, xph)
    fxmh = evaluate(equation, xmh)
    if fxph==None or fxmh==None: return None
    return (fxph - fxmh) / (2 * h)

def secondDerivative(equation, x):
    h, xph, xmh = getDerivativeConsts(x)
    fx = evaluate(equation, x)
    fxph = evaluate(equation, xph)
    fxmh = evaluate(equation, xmh)
    if fx==None or fxph==None or fxmh==None: return None

    return (fxph - 2*fx + fxmh) / (h**2)

def newtonsMethod(equation, x0, epsilon1=1e-12, epsilon2=1e-12):
    maxIters = 1000
    x=x0
    for _ in range(maxIters):
        prevx = x
        numerator = evaluate(equation, x)
        if numerator == 0:
            return x
        denominator = firstDerivative(equation, x)
        if denominator == 0 or numerator == None or denominator == None:
            return None
        x -= (numerator/denominator)
    if abs(numerator) < epsilon1 or abs(prevx-x) < epsilon2:
        return x
    return None

def halleysMethod(equation, x0, epsilon1=1e-12, epsilon2=1e-12):
    maxIters = 500
    x=x0
    for _ in range(maxIters):
        prevx = x
        fx = evaluate(equation, x)
        if fx == 0:
            return x
        firstD = firstDerivative(equation, x)
        secondD = secondDerivative(equation, x)
        if None in (fx, firstD, secondD):
            return None
        numerator = 2 * fx * firstD
        denominator = 2*pow(firstD, 2) - (fx*secondD)
        if numerator == 0 or denominator == 0:
            return None
        x -= numerator/denominator
    if abs(numerator) < epsilon1 or abs(prevx-x) < epsilon2:
        return x
    return None

def makeInitialGuesses(equation):
    rangeOfPowers = 2
    base = 5 
    initials = [0]
    
    for i in range(-rangeOfPowers, rangeOfPowers+1):
        initials += [base**i, -base**i] # 5 seems to be much more well behaved than 10
    
    valids = []
    for i in initials:
        inDomain = (evaluate(equation, i) != None)
        validDerivative = (firstDerivative(equation, i) != None)
        # if the guess can survive at least one iteration of the Newton's method, 
        # allow it
        if inDomain and validDerivative:
            valids.append(i)
            
    return sorted(valids, key=abs)

def solve(equation, found=None):
    if found == None:
        found = []
    guesses = makeInitialGuesses(equation)
    for i in guesses:
        result = newtonsMethod(equation, i)
        if result == None:
            continue
        found.append(result)
        divided = applyDivision(equation, result)
        break
    
    # If we came out of the loop without a result, return found values.
    else: 
        return found

    # If we've found a lot of roots, don't bother with anymore.
    if len(found) >= 10:
        print("Max number of roots reached, stopping search")
        return found

    # Divide function by a root and continue
    return solve(divided, found)

def printRoots(equation, solutions, evalonly=False):
    if evalonly:
        imagcomponent = solutions.imag if abs(solutions.imag) > 1e-20 else 0
        print(f"Value of expression: {solutions.real+0.0}{'+' if imagcomponent > 0 else ''}{f'{imagcomponent+0.0}i' if imagcomponent != 0 else ''}")
        return
    # Sort roots by absolute value and remove insanity values
    solutions = sorted(list(set([i for i in solutions if abs(evaluate(equation, i)) < 1e-10])), key=abs)
    realsolutions, complexsolutions = [], []
    for i in solutions:
        if abs(i.imag) < 1e-10:
            realsolutions.append(f"{round(i.real, 6)+0.0}")
        else:
            imaginary = round(i.imag, 6)+0.0
            complexsolutions.append(f"{round(i.real, 6)+0.0}{'+' if imaginary > 0 else ''}{imaginary}i")
    realsolutions = ", ".join(realsolutions)
    complexsolutions = ", ".join(complexsolutions)
    if complexsolutions:
        print(f"{f'Real solutions:\nx = {realsolutions}' if realsolutions else ''}\nComplex solutions:\nx = {complexsolutions}")
    else:
        print(f"Solutions found:\nx = {realsolutions}")

def main():
    while True:
        eq,evalonly = getInput()
        if evalonly:
            roots = evaluate(eq, None)
            if roots == None:
                print("Invalid expression.")
                continue
        else:
            roots = solve(eq)
            if roots == []:
                print("Can't solve.")
                continue
        print("pre-processing solution list:", roots)
        print()
        printRoots(eq, roots, evalonly)
##        while True:
##            again = input("\nAnother equation? (y/n)\t").lower().strip()
##            if again in {"y", "yes"}:
##                print()
##                break
##            elif again in {"n", "no"}:
##                print("bye")
##                return
##            else:
##                print("Didn't understand.")

if __name__ == "__main__":
    main()
