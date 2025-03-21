import regex as re
from math import *
import ast
import math
import cmath as c

pow = __builtins__.pow

# Get all names from math module
math_names = {name for name in dir(math)}
cmath_names = {name for name in dir(c)}
builtins = {"abs", "c"}
math_names = math_names.union(builtins).union(cmath_names)

epsilon = 2.220446049250313e-16
sqrtepsilon = 1.4901161193847656e-08 # Square root of Python epsilon

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
    pattern = re.compile(r'(\w*\((?:[^()]++|(?1))*+\)|\b[a-zA-Z0-9_\.]+\b|\d+\.\d+|\d+)\*\*(-?\w*\((?:[^()]++|(?1))*+\)|-?\b[a-zA-Z0-9_.]+\b|-?\d+\.\d*|\d+)')
    # Convert ** operator to pow function - seems much faster
    while '**' in expression:
        expression = pattern.sub(r'pow(\1,\2)', expression)
    return expression

def insert_multiplication_signs(equation):
    # Replace terms like "2x" with "2*x"
    equation = re.sub(r'(\d)(x)', r'\1*\2', equation)
    equation = re.sub(r'(x)(\d)', r'\1*\2', equation)
    equation = re.sub(r'(?<![a-z])\b(\d+)(\()', r'\1*\2', equation)
    equation = re.sub(r'(\))(\d)', r'\1*\2', equation)
    # Replace terms like "2sin(x)" with "2*sin(x)"
    # Don't replace a number followed by "j" because that's python's imaginary number
    equation = re.sub(r'(\d)([a-ik-z])', r'\1*\2', equation)
    # Handle cases like (x)(x) and sin(x)x
    equation = re.sub(r'(\))(\()', r'\1*\2', equation)
    equation = re.sub(r'(x)([a-z])', r'\1*\2', equation)
    equation = re.sub(r'(\))([a-z])', r'\1*\2', equation)
    equation = re.sub(r'(?<![a-z])(x)(\()', r'\1*\2', equation)
    return equation

def getInput():
    while True:
        equation = input("\nEnter an equation in terms of x, or an expression without an equals sign or variables:\n")
        equation = equation.strip().lower().replace(" ","").replace("^","**")
        equation = insert_multiplication_signs(equation)
        equation = replace_exponentiation(equation)
        eq = checkInput(equation)
        if eq is None:
            continue
        out, onlyeval = eq[0].split("="), eq[1]
        out = equation if onlyeval else f"({out[0]})-({out[1]})"
        print(f"\nInterpreted {'expression' if onlyeval else 'equation'}: {out}{'' if onlyeval else ' = 0'}\n")
        return out, onlyeval

def checkInput(equation):
    onlyeval = False if "=" in equation else True
    if onlyeval:
        if not(bracketCheck(equation)):
            print("Incorrect brackets.")
            return None
        try:
            names = set(node.id for node in ast.walk(ast.parse(equation)) if isinstance(node, ast.Name))
        except Exception as e:
            print("Invalid formatting. Returned error:", e)
            return None
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
        
        # Extract variable names
        try:
            names = set(
                node.id for node in ast.walk(ast.parse(separate[0])) if isinstance(node, ast.Name)
            ).union(
                node.id for node in ast.walk(ast.parse(separate[1])) if isinstance(node, ast.Name)
            )
        except Exception as e:
            print("Invalid formatting. Returned error:", e)
            return None
        
        if names - math_names != {"x"}:
            print("Invalid variable(s) or function(s).")
            return None
    
        for i in names:
            if i in {"log", "log10", "log2"}:
                print("Note: logs tend to be unstable with Newton's method. Try converting to exponential form if possible.")

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
    return h, x + h, x - h

def firstDerivative(equation, x):
    h, xph, xmh = getDerivativeConsts(x)
    fxph = evaluate(equation, xph)
    fxmh = evaluate(equation, xmh)
    if fxph==None or fxmh==None: return None
    return (fxph - fxmh) / (2 * h)

def newtonsMethod(equation, x0, epsilon1=1e-12, epsilon2=1e-12):
    maxIters = 1000
    x=x0
    change = float('inf')
    for iter in range(maxIters):
        if change == 0: break # 0 change
        if x != x: # NaN
            print("NaN after", iter, "iterations")
            return None
        numerator = evaluate(equation, x)
        if numerator == 0:
            print("\nACCEPTED exact zero at x =", x, "after", iter, "iterations\n")
            return x
        denominator = firstDerivative(equation, x)
        if denominator == 0:
            print("denom zero at x =", x, end=" ")
            if abs(change) <= epsilon2:
                print("was converging, accepted")
                return x
            print("convergence was too slow, change was", change, "eval", numerator)
            return None
        if numerator == None or denominator == None:
            print("invalid at x =", x, numerator, "/", denominator)
            return None
        change = numerator/denominator
        x -= change
    if abs(numerator) <= epsilon1 or abs(change) <= epsilon2:
        print("\nACCEPTED x =", x, "eval was", numerator, "change was", change, "after", maxIters, "iterations\n")
        return x
    print("x =", x, "ran out of iterations, evaled to", numerator, "final change was", change)
    return None

def makeInitialGuesses(equation):
    rangeOfPowers = 2
    base = 5 # 5 seems to be much more well behaved than 10
    initials = [0, 1+1j, 1-1j]
    
    for i in range(-rangeOfPowers, rangeOfPowers+1):
        initials += [base**i, -base**i]
    
    valids = []
    for i in initials:
        inDomain = (evaluate(equation, i) != None)
        validDerivative = (firstDerivative(equation, i) != None)
        # if the guess can survive at least one iteration of the Newton's method, 
        # allow it
        if inDomain and validDerivative:
            valids.append(i)
    
    # If we couldn't find a valid initial guess, make one
    guess = 1
    while (guess <= 1e50):
        if evaluate(equation, guess) != None and firstDerivative(equation, guess) != None:
            valids.append(guess)
            break
        if guess < 0:
            guess *= -10
        else:
            guess *= -1
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
        print(f"Value of expression: {solutions.real}{'+' if imagcomponent > 0 else ''}{f'{imagcomponent}i' if imagcomponent != 0 else ''}")
        return
    # Sort roots by absolute value and remove insanity values
    highvals = sorted(list(set([round(i.real,5)+round(i.imag,5)*1j for i in solutions if abs(i) >= 1e10 and abs(evaluate(equation, i)) < 1e-8])), key=abs)
    solutions = sorted(list(set([round(i.real,5)+round(i.imag,5)*1j for i in solutions if (abs(evaluate(equation, i)) < 1e-10) and (abs(i) < 1e10)])), key=abs)
    print(solutions)
    realsolutions, complexsolutions = [], []
    for i in solutions:
        print("solution", i, "triggered", end=" ")
        if abs(i.imag) < 1e-20:
            print("real solution code")
            realsolutions.append(f"{i.real}")
        else:
            print("imaginary solution code")
            imaginary = round(i.imag,5)
            complexsolutions.append(f"{i.real}{'+' if imaginary > 0 else '-'}{abs(imaginary) if abs(imaginary) != 1 else ''}i")
    realsolutions = ", ".join(realsolutions)
    complexsolutions = ", ".join(complexsolutions)
    print()
    if complexsolutions:
        print(f"{f'Real solutions:\nx = {realsolutions}' if realsolutions else ''}\nComplex solutions:\nx = {complexsolutions}")
    else:
        print(f"Solutions found:\nx = {realsolutions}")
    
    if len(highvals) > 0:
        formatted_highvals = []
        for i in highvals:
            imagcomponent = i.imag if abs(i.imag) > 1e-20 else 0
            formatted_highvals.append(f"{round(i.real,5)+0.0}{'+' if imagcomponent > 0 else ''}{f'{imagcomponent+0.0}i' if imagcomponent != 0 else ''}")
        
        print(f"\nAlso found the following large solutions:\nx = {', '.join(formatted_highvals)}")

def main():
    while True:
        eq,evalonly = getInput()
        if evalonly:
            roots = evaluate(eq, None)
            try:
                abs(roots)
            except:
                print("Input invalid or out of domain.")
                continue
        else:
            outs = solve(eq)
            roots = []
            for i in outs:
                try:
                    abs(i)
                except:
                    continue
                else:
                    roots.append(i)
            if roots == []:
                print("No solutions found.")
                continue
        print("pre-processing solution list:", roots)
        print()
        printRoots(eq, roots, evalonly)

if __name__ == "__main__":
    main()
