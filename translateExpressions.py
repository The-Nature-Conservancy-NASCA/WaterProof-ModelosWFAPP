from sympy import *
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import parse_expr
import re
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

def eval_function(expr):
    latex_expr = expr.replace(" }", "}")
    re_expr_brackets = r"\{([A-Za-z]+)\}"
    result = re.findall(re_expr_brackets, latex_expr)

    wp_vars = {
        'WPr' : '2000',
        'WNr' : '4000',
        'WsedR' : '1000',
        'QCINFRA' : '1000',
        'QCSINFRA' : '1000',
        'CsedCsinfraInput' : '1000',
        'CNCsinfrainput' : '1000',
        'Csed' : '1000',
        'Q' : '1000',
        'CN' : '1000',
    }

    for r in result:
        replace_str = r"\mathrm{}" .format("{" + r + "}")
        print ("replacing ::" +  replace_str)
        latex_expr = latex_expr.replace(replace_str,wp_vars[r])
        # latex_expr = latex_expr.replace(r, wp_vars[r])

    for v in wp_vars:
        latex_expr = latex_expr.replace(v,wp_vars[v])

    #dict_eval = {}
    #dict_eval = {result[i]:result[i] for i in range(0,len(result),1)}
    print ("latex_expr ::")
    print (latex_expr)
    #try:
    expr_parse = parse_latex(latex_expr)
    result_eval = eval(str(expr_parse))    
    return expr_parse, result_eval
    #except Exception as e:
    #    return 'Error parsing expression :: ' + str(e), -99999
    #print("expr_parse ::")
    #print(str(expr_parse))
    


latex_expr = r"\min \left(\left(0.8515\cdot \mathrm{WPr }\cdot \left(\frac{\left(1\cdot 10^3\right)}{31536}\right)\right),\left(0.0532\cdot \mathrm{WNr }\cdot \left(\frac{\left(1\cdot 10^3\right)}{31536}\right)\right)\right)"

res_water_row_latex_expr = r"\left(\left(-5.064\cdot 10^{-4}\right)\cdot \left(0.315\cdot \mathrm{WsedR}\cdot \left(\frac{1\cdot 10^6}{31536}\right)\right)^2\right)+\left(126.6\cdot \left(0.315\cdot \mathrm{WsedR}\cdot \left(\frac{1\cdot 10^6}{31536}\right)\right)\right)"
pilimoero_latex_expr = r"\left(\left(-4.4\cdot10^{-8}\right)\cdot QCINFRA^3+\left(0.00111\cdot QCSINFRA^2\right)+\left(3.756\cdot QCSINFRA\right)+29338\right)\cdot\left(1+\left(0.24\cdot\left(\frac{CsedCsinfraInput^{-56}}{56}\right)\right)+\left(0.06\cdot\left(\frac{CNCsinfrainput^{-20}}{20}\right)\right)\right)"
#latex_expr = r"\min \left(\left(0.8515\cdot a\cdot \left(\frac{\left(1\cdot 10^3\right)}{31536}\right)\right),\left(0.0532\cdot b\cdot \left(\frac{\left(1\cdot 10^3\right)}{31536}\right)\right)\right)"

test_exp = r"\left(\left(\left(2.25\cdot 10^{74}\right)\cdot \left(Q_{csin fra^{^3}}\right)-\left(4.44\cdot 10^{^{-6}}\right)\cdot Qc\sin fra^{^2}\right)+\left(41.27\cdot Qc\sin fra\right)+8625\right)\cdot \left(1+\left(0.24\cdot \left(\frac{Csed_{C\sin fraInput^{^{-56}}}^{ }}{56}\right)\right)+\left(0.06\cdot \left(CN_{\frac{C\sin fraInput^{^{-20}}}{20}}\right)\right)\right)"
bombeo_expr = r"\left(\left(11126.6\cdot Q\right)+30929.7\right)\cdot \left(1+\left(0.24\cdot \left(\frac{Csed-56}{56}\right)\right)+\left(0.06\cdot \left(\frac{CN-20}{20}\right)\right)\right)"
exp, result = eval_function(bombeo_expr)
print("result :: ")
print(exp)
print(result)