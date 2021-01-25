from sympy import *
from sympy.parsing.latex import parse_latex
# from latex2sympy import *

# x = symbols('Q')
# Cs = symbols('CSed')
# Cn = symbols('CN')
Q = 1
Csed = 2
CN = 3


# xml = r'{({(11126.6{Q})}+30939.7)}1+{(0.24{(\frac{{\mathit{Csed}}-56}{56})})}+{(0.06{(\frac{\mathit{CN}-20}{20})})}'
xml = r'\left(\left(11126.6\cdot\mathit{Q}\right)+30939.7\right)\cdot1+\left(0.24\cdot\frac{\left(\left(\mathit{CSed}\right)-56\right)}{56}\right)+\left(0.06\cdot\left(\frac{\mathit{CN}-20}{20}\right)\right)'
# expr = process_sympy(xml)
expr = parse_latex(xml)
# print(expr)
dictEval = dict(
    Q = Q,
    CSed = Csed,
    CN = CN
)
result = expr.evalf(10, subs=dictEval)
print("Expr:" + str(expr))
print("Result: " + str(result))
# print(expr.evalf(10, subs=dict(q=5, s=2, n=3)))