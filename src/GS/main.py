from typing import List
import numpy as np
from elements import vector_element_pair, vector_extended_pair


class Proof():
    def __init__(self, equations: List[Equation], witness):
        pass

    def serialize(self):
        '''
        returns thetha, pi, c vector & d vector
        '''
        pass



class PairExpr():
    def __init__(self):
        pass


class Equation():
    def __init__(self, x, y, a, b, Gamma, t, eq_type=None):
        self.type = eq_type

        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.Gamma = Gamma
        self.t = t

    def _is_correct(self):
        return vector_element_pair(self.a, self.y) + vector_element_pair(self.x, self.b) + vector_element_pair(self.x, self.Gamma @ self.y) == self.t
