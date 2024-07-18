import regex as re
from math import *
import ast
import math
import cmath as c

# Get all names from math module
math_names = {name for name in dir(math)}
cmath_names = {name for name in dir(c)}

epsilon = 2.220446049250313e-16
sqrtepsilon = 1.4901161193847656e-08 # Square root of Python epsilon

builtins = {"abs", "c"}
undesired = {"log10", "atan2"}
math_names = math_names.union(builtins).union(cmath_names)#.difference(undesired)

def sgn(x):
    return 1 if x > 0 else -1 if x < 0 else 0

def bracketCheck(expression):
    # Check if brackets are valid
    stack = []
    brackets = {'(': ')', '{': '}', '[': ']'}
    for char in expression:
        if char in brackets:
            stack.append(char)
        elif char in brackets.values():
            if not stack or brackets[stack.pop()]!= char:
                return False
    return not stack

def replace_exponentiation(expression):
    # Regex pattern to match the base and exponent of ** operator
    pattern = re.compile(r'(-?\([^()]+\)|-?\b\w+\b|\d+\.+\d+|\d+|-?\b\w+\((?:[^()]+)*\))\*\*(-?\b\w+\((?:[^()]+|(?1))*\)|-?\([^()]+\)|-?\d+\.+\d*|-?\b\w+\b)')
    
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
    equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)
    # Handle cases like (x)(x) and sin(x)x
    equation = re.sub(r'(\))(\()', r'\1*\2', equation)
    equation = re.sub(r'(x)([a-zA-Z])', r'\1*\2', equation)
    equation = re.sub(r'(\))([a-zA-Z])', r'\1*\2', equation)
    # equation = re.sub(r'([a-zA-Z])(\()', r'\1*\2', equation)
    # equation = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', equation)
    return equation

def getInput():
    while True:
        equation = input("\nEnter an equation in terms of x:\n").strip().lower().replace(" ","").replace("^","**")
        equation = replace_exponentiation(equation)
        equation = insert_multiplication_signs(equation)
        eq = checkInput(equation)
        if eq is None:
            continue
        onlyeval = eq[1]
        out = eq[0].split("=")
        out = f"({out[0]})-({out[1]})" if not(onlyeval) else equation
        print("Interpreted equation:", equation)
        print(out)
        print()
        return out, onlyeval

def checkInput(equation):
    onlyeval = False
##    if "=" not in equation:
##        print("Missing an equals sign.")
##        return None
    
##    if "x" not in equation:
##        print("No x-variable to solve for.")
##        return None
        
    separate = equation.split("=")
    if len(separate) > 2:
        print("Only one equals sign allowed.")
        return None
    elif len(separate) == 1:
        onlyeval = True
        
    if "" in separate:
        print("Empty left or right side.")
        return None

    for part in separate:
        if not bracketCheck(part):
            print("Incorrect brackets.")
            return None

    # Extract variable names
    names = set(
        node.id for node in ast.walk(ast.parse(separate[0])) if isinstance(node, ast.Name)
    ).union(
        node.id for node in ast.walk(ast.parse(separate[1])) if isinstance(node, ast.Name)
    ) if not onlyeval else set(
        node.id for node in ast.walk(ast.parse(separate[0])) if isinstance(node, ast.Name)
    )

    for i in names:
        if i in {"log"}:
            print("Note: using logs can'sudoku_solver_refactor.py")
        elif i in undesired:
            print(i, "is an unsupported function.")
            return None
    # Remove math module names from the set of names
    print(names)
    names -= math_names
    print(names)
##    if names != {"x"} or names != set():
##        print("Incorrect variable usage.")
##        return None

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

def newtonsMethod(equation, x0, epsilon1=1e-10, epsilon2=1e-10):
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
    if abs(numerator) < epsilon*abs(numerator) or abs(prevx-x) < epsilon*abs(prevx-x):
        return x
    return None

def halleysMethod(equation, x0, epsilon1=1e-10, epsilon2=1e-10):
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
    if abs(numerator) < epsilon*abs(numerator) or abs(prevx-x) < epsilon*abs(prevx-x):
        return x
    return None

def makeInitialGuesses(equation):
    inipowers = 2
    initials = [0]
    
    for i in range(-inipowers, inipowers+1):
        initials += [5**i, -5**i] # 5 seems to be much more well behaved than 10
    
    reals = []
    for i in initials:
        inDomain = (evaluate(equation, i) != None)
        validDerivative = (firstDerivative(equation, i) != None)
        if inDomain and validDerivative:
            reals.append(i)
            
    return sorted(reals, key=abs)
    
def solve(equation, found=None):
    if found == None:
        found = []
    guesses = makeInitialGuesses(equation)
    for i in guesses:
        result = None
        try:
            result = halleysMethod(equation, i) # try halley's method
        except:
            pass
        if result == None:
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
        return found

    # Divide function by a root and continue
    return solve(divided, found)

def main():
    while True:
        eq,evalonly = getInput()
        if evalonly:
            roots = evaluate(eq, 0)
        else:
            roots = solve(eq)
        if roots == []:
            print("Can't solve.")
            continue
        print(roots)
        roots = sorted(list(set(roots)), key=abs)
        realroots = [f"{round(i, 6)+0.0}" for i in roots]
        realroots = ", ".join(realroots)
        print(f"Roots found:\nx = {realroots}")
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
