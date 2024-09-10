from framework import load_element, load_crs, vars_array, Equation, equations, proof

CRS = load_crs()

X = []
Y = []
x = []
y = []

eqs = equations()
const = []

sigma = load_element('sigma', 1)
X.append(('sigma', sigma))

pkg = load_element('pkg', 2)
const['pkg'] = pkg

t = load_element('t', 3)
const['t'] = t

eq = Equation([], [pkg], [[]], t, 3)
eqs.append(eq)
variables = vars_array(X,Y,x,y)
proof(CRS, eqs, variables)