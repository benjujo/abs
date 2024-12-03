
from framework import load_element, load_crs, Equation, equations, proof
from utils import NamedArray

CRS = load_crs()

X = NamedArray([])
Y = NamedArray([])
x = NamedArray([])
y = NamedArray([])

eqs = equations()
const = {}

z = load_element('z', 0)
x = x.append('z', z)

a = load_element('a', 0)
const['a'] = a

t = load_element('t', 0)
const['t'] = t

eq = Equation([], [a], [[]], t, 0)
eqs.append(eq)
p=proof(CRS, eqs, X, Y, x, y)
