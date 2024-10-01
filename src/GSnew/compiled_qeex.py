
from framework import load_element, load_crs, vars_array, Equation, equations, proof

CRS = load_crs()

X = []
Y = []
x = []
y = []

eqs = equations()
const = {}

z = load_element('z', 0)
x.append(('z', z))

a = load_element('a', 0)
const['a'] = a

t = load_element('t', 0)
const['t'] = t

eq = Equation([], [a], [[]], t, 0)
eqs.append(eq)
variables = vars_array(X,Y,x,y)
p=proof(CRS, eqs, variables)
