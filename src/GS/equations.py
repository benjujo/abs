from elements import *

EQUATION_TYPES = {
    'PPE': 3,
    'MSE1': 1,
    'MSE2': 2,
    'QE': 0
}

class Equation():
    def __init__(self, eq_type: int):
        self.type = eq_type

    def to_proof(self):
        pi = 0
        theta = 0



class PPEEquation(Equation):
    def __init__(self):
        super().__init__(EQUATION_TYPES['PPE'])
