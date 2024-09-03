
from nodes import *
from framework import load_element, load_crs, proof, Variable, Constant

CRS = load_crs()

X = ['sigma']
Y = []
x = []
y = []

eqs = []
vars = {}

sigma = Variable(load_element(sigma, 1), 1)
vars['sigma'] = sigma

pkg = Constant(load_element(pkg, 2))
const['pkg'] = pkg

t = Constant(load_element(t, 3))
const['t'] = t

eqs.append(([], ['pkg'], [], t))
proof(CRS, eqs, X, Y, x, y)