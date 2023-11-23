from equations import Equation

from typing import List

class Proof():
    def __init__(self):
        # TODO: Create CRS Setup
        pass

    def prove(self, equations: List[Equation]):
        vars = {}
        for eq in equations:
            vars.update(eq.extract_variables())
        
        for var in vars:
            comm, R = var.commit()

    def verify(self):
        pass
