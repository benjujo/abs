
from nodes import *
from framework import load_element, load_crs, proof, Variable, Constant

CRS = load_crs()

X = [<nodes.VariableG1Node object at 0x7feb7af96850>]
Y = []
x = []
y = []

eqs = []

sigma = Variable(load_element(sigma, 1), 1)
vars['sigma'] = sigma

pkg = Constant(load_element(pkg, 2))
const['pkg'] = pkg

t = Constant(load_element(t, 3))
const['t'] = t

eqs.append(([], ['pkg'], [], t))
proof(CRS, eqs, X, Y, x, y)