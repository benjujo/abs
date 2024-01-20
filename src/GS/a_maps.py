from .elements import ZpElement
from .a_elements import A, Constant, Variable
from .b_elements import B1, B2, Commit
from typing import List, Dict, Tuple


class AMap():
    def __init__(self, a1: A, a2: A):
        self.a1 = a1
        self.a2 = a2
        self.theta_dim = 0 # When _validate is called, this is set
        self.pi_dim = 0 # When _validate is called, this is set
    
    def _validate(self, eq_type):
        # TODO: Run validations if the instance is correct
        self.a1.position = 1
        self.a2.position = 2

    def theta(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        return NotImplemented

    def pi(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        return NotImplemented

    def eval_lhs(self, comms: Dict[str, Commit], CRS):
        return NotImplemented

class AMapLeft(AMap):
    # TODO: Check types
    def __init__(self, a1: Variable, a2: Constant):
        super().__init__(a1, a2)

    def theta(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        return [B1.zero()] * self.theta_dim


    def pi(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        var = variables[self.a1.name]
        com = comms[self.a1.name]

        r = com.r

        res = []
        for i in r:
            res.append(i * self.a2.iota(CRS))

        return res

    def eval_lhs(self, comms: Dict[str, Commit], CRS):
        return comms[self.a1.name].b.extended_pair(self.a2.iota(CRS))
    
    def eval(self, variables: Dict[str, Variable]):
        left = variables[self.a1.name].element
        right = self.a2.element
        return left.pair(right)


class AMapRight(AMap):
    # TODO: Check types
    def __init__(self, a1: Constant, a2: Variable):
        super().__init__(a1, a2)

    def theta(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        var = variables[self.a2.name]
        com = comms[self.a2.name]

        r = com.r

        res = []
        for i in r:
            res.append(i * self.a1.iota(CRS))

        return res

    def pi(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        return [B2.zero()] * self.pi_dim
    
    def eval_lhs(self, comms: Dict[str, Commit], CRS):
        return self.a1.iota(CRS).extended_pair(comms[self.a2.name].b)
    
    def eval(self, variables: Dict[str, Variable]):
        left = self.a1.element
        right = variables[self.a2.name].element
        return left.pair(right)


class AMapBoth(AMap):
    # TODO: Check types
    def __init__(self, a1: Variable, a2: Variable, gamma=ZpElement.init(1)):
        self.gamma = gamma
        super().__init__(a1, a2)

    def theta(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        varx = variables[self.a1.name]
        comx = comms[self.a1.name]
        vary = variables[self.a2.name]
        comy = comms[self.a2.name]

        rx = comx.r
        ry = comy.r

        res = []
        for i in ry:
            res.append(i * self.gamma * varx.iota(CRS))

        return res

    def pi(self, comms: Dict[str, Commit], variables: Dict[str, Variable], CRS):
        varx = variables[self.a1.name]
        comx = comms[self.a1.name]
        vary = variables[self.a2.name]
        comy = comms[self.a2.name]

        rx = comx.r
        ry = comy.r

        Sv = B2.zero()
        for i in range(len(ry)):
            Sv += ry[i] * CRS['v'][i]

        res = [] 
        for i in rx:
            #res.append(i * self.gamma * vary.iota(CRS)) Así arrojaba false...
            res.append(i * self.gamma * vary.iota(CRS) + i * self.gamma * Sv)



        return res
    
    def eval_lhs(self, comms: Dict[str, Commit], CRS):
        return comms[self.a1.name].b.extended_pair(self.gamma * comms[self.a2.name].b)
    
    def eval(self, variables: Dict[str, Variable]):
        left = variables[self.a1.name].element
        right = variables[self.a2.name].element
        return left.pair(right)


class AMapNone(AMap):
    # TODO: Check types
    def eval(self, variables: Dict[str, Variable]):
        left = self.a1.element
        right = self.a2.element
        return left.pair(right)
