
from framework import load_element, load_crs, Equation, equations, proof
from utils import NamedArray

CRS = load_crs()

X = NamedArray([])
Y = NamedArray([])
x = NamedArray([])
y = NamedArray([])

eqs = equations()
const = {}

sigma = load_element('sigma', 1)
X = X.append('sigma', sigma)

pkg = load_element('pkg', 2)
const['pkg'] = pkg

t = load_element('t', 3)
const['t'] = t

eq = Equation([], [pkg], [[]], t, 3)
eqs.append(eq)
p=proof(CRS, eqs, X, Y, x, y)
