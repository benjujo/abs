from elements import *
from typing import List


EQUATION_TYPES = {
    'PPE': 3,
    'MS1E': 1,
    'MS2E': 2,
    'QE': 0
}


class MapA():
    def __init__(self, a_1, a_2, gamma):
        self.a_1 = a_1
        self.a_2 = a_2
        self.gamma = gamma
    
    def _validate(self):
        # TODO: Run validations if the instance is correct
        pass

    def _eval(self):
        return element_pair(self.a_1.element, self.a_2.element)

    def extract_variables(self):
        vars = {}
        if isinstance(self.a_1, Variable):
            vars.update({self.a_1.name: self.a_2})
        if isinstance(self.a_2, Variable):
            vars.update({self.a_2.name: self.a_2})
        return vars

    

class MapB(b_1, b_2):

    def eval(self):
        return extended_pair(b_1, b_2)


class Commitment():
    def __init__(self, variable: Variable):
        self.variable = variable

    @property
    def a_i(self):
        return self.variable.a_i

    

class Variable():
    def __init__(self, name:str, element:Element, a_i=None):
        self.name = name
        self.element = element
        self.a_i = a_i
        self.commitment = None

    def commit(self):
        return self.element.commit(self.a_i)

class Constant():
    def __init__(self, name:str, element:Element, a_i=None):
        self.name = name
        self.element = element
        self.a_i = a_i

class Equation():
    def __init__(self, map_as: List[MapA], t, eq_type):
        self.type = eq_type

        self.map_as = map_as

    def extract_variables(self):
        eq_vars = {}
        for map_a in self.map_as:
            eq_vars.update(map_a.extract_variables())
        return eq_vars

        

    def _is_correct(self):
        return vector_element_pair(self.a, self.y) + vector_element_pair(self.x, self.b) + vector_element_pair(self.x, self.Gamma @ self.y) == self.t




class PPEquation(Equation):
    def __init__(self):
        super().__init__(EQUATION_TYPES['PPE'])
