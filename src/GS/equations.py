from .elements import *
from .a_elements import A, Constant, Variable
from .b_elements import B, B1, B2, BT, Commit
from .a_maps import AMap, AMapLeft, AMapRight, AMapBoth
from typing import List, Dict, Tuple
from functools import reduce


EQUATION_TYPES = {
    'PPE': 3,
    'MS1E': 1,
    'MS2E': 2,
    'QE': 0
}

B_DICT = {
    1: B1,
    2: B2
}


class Equation():
    def __init__(self, name:str, a_maps: List[AMap], target:Constant, eq_type):
        self.name = name

        self.type = eq_type
        self.a_maps = a_maps
        self.target = target

        for a_map in a_maps:
            a_map.theta_dim = self.theta_dim
            a_map.pi_dim = self.pi_dim

    def _validate(self):
        # TODO: Complete
        for a_map in self.a_maps:
            a_map._validate(self.type)


    def check(self, variables: List[Variable]) -> bool:
        # TODO: Check if the equation is valid. Return True or False
        return True

    def prove(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS) -> Tuple[List[B1], List[B2]]:
        self._validate()
        theta = [B1.zero()] * self.theta_dim
        pi = [B2.zero()] * self.pi_dim


        for a_map in self.a_maps:
            partial_theta = a_map.theta(comms, variables, CRS)
            partial_pi = a_map.pi(comms, variables, CRS)

            for i in range(self.theta_dim):
                theta[i] += partial_theta[i]
            
            for i in range(self.pi_dim):
                pi[i] += partial_pi[i]

        return theta, pi

    def verify(self, comms: Dict, theta: List[B1], pi: List[B2], CRS):
        lhs = BT.zero()

        for a_map in self.a_maps:
            lhs += a_map.eval_lhs(comms, CRS)

        rhs = self.target._iotat(CRS, self.type)

        for i in range(self.pi_dim):
            rhs += CRS['u'][i].extended_pair(pi[i])
        for i in range(self.theta_dim):
            rhs += theta[i].extended_pair(CRS['v'][i])

        return lhs == rhs

    @property
    def theta_dim(self):
        return NotImplemented

    @property
    def pi_dim(self):
        return NotImplemented


class PPEquation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:Constant):
        super().__init__(name, a_maps, target, EQUATION_TYPES['PPE'])

    @property
    def theta_dim(self):
        return 2

    @property
    def pi_dim(self):
        return 2


class MS1Equation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:Constant):
        super().__init__(name, a_maps, target, EQUATION_TYPES['MS1E'])

    @property
    def theta_dim(self):
        return 1

    @property
    def pi_dim(self):
        return 2


class MS2Equation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:Constant):
        super().__init__(name, a_maps, target, EQUATION_TYPES['MS2E'])

    @property
    def theta_dim(self):
        return 2

    @property
    def pi_dim(self):
        return 1


class QEquation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:Constant):
        super().__init__(name, a_maps, target, EQUATION_TYPES['QE'])

    @property
    def theta_dim(self):
        return 1

    @property
    def pi_dim(self):
        return 1

