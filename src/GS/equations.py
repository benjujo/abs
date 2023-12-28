from .elements import *
from typing import List, Dict, Tuple
from functools import reduce


EQUATION_TYPES = {
    'PPE': 3,
    'MS1E': 1,
    'MS2E': 2,
    'QE': 0
}


class A():
    def __init__(self, is_witness: bool):
        self.is_witness = is_witness

    def iota(self, CRS):
        if self.position == 1 or self.element.type == G1:
            return self._iota1(CRS)
        elif self.position == 2 or self.element.type == G2:
            return self._iota2(CRS)
        raise Exception('Position not set')

    def _iota1(self, CRS):
        if self.element.type == ZR:
            u = CRS['u2'] + B1(G1Element.zero(), CRS['u1'].e1) # u1.e1 is p1
            return self.element * u
        
        return B1(G1Element.zero(), self.element)

    def _iota2(self, CRS):
        if self.element.type == ZR:
            v = CRS['v2'] + B2(G2Element.zero(), CRS['v1'].e1) # v1.e1 is p2
            return self.element * v
        
        return B2(G2Element.zero(), self.element)

    def _iotat(self, CRS, eq_type):
        if eq_type == EQUATION_TYPES['PPE']:
            return BT(GTElement.zero(), GTElement.zero(),
                      GTElement.zero(), self.element)
        if eq_type == EQUATION_TYPES['MS1E']:
            v = CRS['v2'] + B2(G2Element.zero(), CRS['v1'].e1)
            return self.element.iota(CRS).extended_pair(v)
        if eq_type == EQUATION_TYPES['MS2E']:
            u = CRS['u2'] + B1(G1Element.zero(), CRS['u1'].e1)
            return u.extended_pair(self.element.iota(CRS))
        if eq_type == EQUATION_TYPES['QE']:
            u = CRS['u2'] + B1(G1Element.zero(), CRS['u1'].e1)
            v = CRS['v2'] + B2(G2Element.zero(), CRS['v1'].e1)
            return u.extended_pair(self.element * v)
        raise Exception('Invalid equation type')
        
    
    @property
    def type(self):
        return self.element.type


class Constant(A):
    def __init__(self, element: Element):
        self.element = element
        super().__init__(False)

    def __json__(self):
        return {'element': self.element}

    @classmethod
    def from_json(cls, json):
        return cls(Element.from_json(json['element']))


class AMap():
    def __init__(self, a1: A, a2: A, gamma):
        self.a1 = a1
        self.a2 = a2
        self.gamma = gamma
        self.theta_dim = 0 # When _validate is called, this is set
        self.pi_dim = 0 # When _validate is called, this is set
    
    def _validate(self, eq_type):
        # TODO: Run validations if the instance is correct
        self.a1.position = 1
        self.a2.position = 2

    def theta(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS):
        return NotImplemented

    def pi(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS):
        return NotImplemented

    def eval_lhs(self, comms: Dict[str, "Commit"], CRS):
        return NotImplemented

class AMapLeft(AMap):
    # TODO: Check types
    def __init__(self, a1, a2):
        super().__init__(a1, a2, None)

    def theta(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS):
        return [B1.zero()] * self.theta_dim


    def pi(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS):
        var = variables[self.a1.name]
        com = comms[self.a1.name]

        r = com.r

        res = []
        for i in r:
            res.append(i * self.a2.iota(CRS))

        return res

    def eval_lhs(self, comms: Dict[str, "Commit"], CRS):
        return comms[self.a1.name].b.extended_pair(self.a2.iota(CRS))
    
    def eval(self, variables: Dict[str, "Variable"]):
        left = variables[self.a1.name].element
        right = self.a2.element
        return left.pair(right)


class AMapRight(AMap):
    # TODO: Check types
    def __init__(self, a1, a2):
        super().__init__(a1, a2, None)

    def theta(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS):
        var = variables[self.a2.name]
        com = comms[self.a2.name]

        r = com.r

        res = []
        for i in r:
            res.append(i * self.a1.iota(CRS))

        return res

    def pi(self, comms: Dict[str, "Commit"], variables: Dict[str, "Variable"], CRS):
        return [B2.zero()] * self.pi_dim
    
    def eval_lhs(self, comms: Dict[str, "Commit"], CRS):
        return self.a1.iota(CRS).extended_pair(comms[self.a2.name].b)
    
    def eval(self, variables: Dict[str, "Variable"]):
        left = self.a1.element
        right = variables[self.a2.name].element
        return left.pair(right)


class AMapBoth(AMap):
    # TODO: Check types
    def __init__(self, a1, a2, gamma):
        super().__init__(a1, a2, gamma)
    
    def eval_lhs(self, comms: Dict[str, "Commit"], CRS):
        return self.gamma * comms[self.a1.name].b.extended_pair(comms[self.a2.name].b)
    
    def eval(self, variables: Dict[str, "Variable"]):
        left = variables[self.a1.name].element
        right = variables[self.a2.name].element
        return left.pair(right)


class AMapNone(AMap):
    # TODO: Check types
    def eval(self, variables: Dict[str, "Variable"]):
        left = self.a1.element
        right = self.a2.element
        return left.pair(right)

    
class B():
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __json__(self):
        return {'e1': self.e1, 'e2': self.e2}

    def extended_pair(self, other):
        return NotImplemented
    
    @classmethod
    def from_json(cls, json):
        return cls(Element.from_json(json['e1']), Element.from_json(json['e2']))
    

class B1(B):
    def __add__(self, other):
        if not isinstance(other, B1):
            return NotImplemented
        return B1(self.e1 + other.e1, self.e2 + other.e2)
    
    def __rmul__(self, other):
        if isinstance(other, ZpElement):
            return B1(other * self.e1, other * self.e2)
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, B1):
            return NotImplemented
        return B1(self.e1 - other.e1, self.e2 - other.e2)

    def extended_pair(self, other):
        if not isinstance(other, B2):
            raise Exception('Invalid type')
        return BT(self.e1.pair(other.e1), self.e2.pair(other.e1),
                  self.e1.pair(other.e2), self.e2.pair(other.e2))
    
    @classmethod
    def zero(cls):
        return cls(G1Element.zero(), G1Element.zero())


class B2(B):
    def __add__(self, other):
        if not isinstance(other, B2):
            return NotImplemented
        return B2(self.e1 + other.e1, self.e2 + other.e2)
    
    def __rmul__(self, other):
        if isinstance(other, ZpElement):
            return B2(other * self.e1, other * self.e2)
        return NotImplemented

    def __sub__(self, other):
        if not isinstance(other, B2):
            return NotImplemented
        return B2(self.e1 - other.e1, self.e2 - other.e2)

    @classmethod
    def zero(cls):
        return cls(G2Element.zero(), G2Element.zero())


class BT:
    def __init__(self, e1, e2, e3, e4):
        self.e1 = e1
        self.e2 = e2
        self.e3 = e3
        self.e4 = e4
    
    def __add__(self, other):
        if not isinstance(other, BT):
            return NotImplemented
        return BT(self.e1 * other.e1, self.e2 * other.e2,
                  self.e3 * other.e3, self.e4 * other.e4)

    def __sub__(self, other):
        if not isinstance(other, BT):
            return NotImplemented
        return BT(self.e1 / other.e1, self.e2 / other.e2,
                  self.e3 / other.e3, self.e4 / other.e4)

    def __eq__(self, other):
        if not isinstance(other, BT):
            return False
        return self.e1 == other.e1 and self.e2 == other.e2 and self.e3 == other.e3 and self.e4 == other.e4

    def __json__(self):
        return {'e1': self.e1, 'e2': self.e2, 'e3': self.e3, 'e4': self.e4}
    
    @classmethod
    def from_json(cls, json):
        return cls(Element.from_json(json['e1']), Element.from_json(json['e2']),
                   Element.from_json(json['e3']), Element.from_json(json['e4']))
    @classmethod
    def zero(cls):
        return cls(GTElement.zero(), GTElement.zero(),
                   GTElement.zero(), GTElement.zero())


class Variable():
    def __init__(self, name: str, element: Element, position: int = None):
        self.name = name
        self.element = element
        self.position = position

    def iota(self, CRS):
        if self.position == 1 or self.element.type == G1:
            return self._iota1(CRS)
        elif self.position == 2 or self.element.type == G2:
            return self._iota2(CRS)
        raise Exception('Position not set')

    def _iota1(self, CRS):
        if self.element.type == ZR:
            u = CRS['u2'] + B1(G1Element.zero(), CRS['u1'].e1) # u1.e1 is p1
            return self.element * u
        
        return B1(G1Element.zero(), self.element)

    def _iota2(self, CRS):
        if self.element.type == ZR:
            v = CRS['v2'] + B2(G2Element.zero(), CRS['v1'].e1) # v1.e1 is p2
            return self.element * v
        
        return B2(G2Element.zero(), self.element)

    def _randomize(self, CRS):
        if self.position == 1 or self.element.type == G1:
            return self._randomize1(CRS)
        elif self.position == 2 or self.element.type == G2:
            return self._randomize2(CRS)
        raise Exception('Position not set')

    def _randomize1(self, CRS):
        if self.element.type == ZR:
            r = ZpElement.random()
            return (r,), r * CRS['u1']
        r1, r2 = [ZpElement.random() for _ in range(2)]
        return (r1, r2), r1 * CRS['u1'] + r2 * CRS['u2']

    def _randomize2(self, CRS):
        if self.element.type == ZR:
            r = ZpElement.random()
            return (r,), r * CRS['v1']
        r1, r2 = [ZpElement.random() for _ in range(2)]
        return (r1, r2), r1 * CRS['v1'] + r2 * CRS['v2']

    def commit(self, CRS):
        r, randomization = self._randomize(CRS)
        return Commit(self.name, self.iota(CRS) + randomization, r)

    def __json__(self):
        return {'name': self.name, 'position': self.position}

    @classmethod
    def from_json(cls, json):
        return cls(json['name'], json['position'])


class Commit():
    def __init__(self, name: str, b: B, r: Tuple[ZpElement, ...]):
        self.name = name
        self.b = b
        self.r = r

    def __json__(self):
        return {'name': self.name, 'b': self.b, 'b_type': type(self.b).__name__}

    @classmethod
    def from_json(cls, json):
        # TODO: dispatch to B1 & B2
        return cls(json['name'], B.from_json(json['b']), None)


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

    def verify(self, comms: Dict, theta: List[B], pi: List[B], CRS):
        lhs = BT.zero()

        for a_map in self.a_maps:
            lhs += a_map.eval_lhs(comms, CRS)

        rhs = self.target._iotat(CRS, self.type)

        for i in range(self.pi_dim):
            rhs += CRS['u'][i].extended_pair(pi[i])
        for i in range(self.theta_dim):
            rhs += theta[i].extended_pair(CRS['v'][i])

        print(f"rhs: {rhs}")
        print(f"lhs: {lhs}")

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
        return 2

    @property
    def pi_dim(self):
        return 1


class MS2Equation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:Constant):
        super().__init__(name, a_maps, target, EQUATION_TYPES['MS2E'])

    @property
    def theta_dim(self):
        return 1

    @property
    def pi_dim(self):
        return 2


class QEquation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:Constant):
        super().__init__(name, a_maps, target, EQUATION_TYPES['QE'])

    @property
    def theta_dim(self):
        return 1

    @property
    def pi_dim(self):
        return 1


B_DICT = {
    1: B1,
    2: B2
}