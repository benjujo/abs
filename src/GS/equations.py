from elements import *
from typing import List, Dict


EQUATION_TYPES = {
    'PPE': 3,
    'MS1E': 1,
    'MS2E': 2,
    'QE': 0
}


class A():
    def __init__(self, is_witness: bool):
        self.is_witness = is_witness
        
    
    @property
    def type(self):
        return self.element.type


class Constant(A):
    def __init__(self, element: Element):
        self.element = element
        super().__init__(False)


class Variable(A):
    def __init__(self, name: str):
        self.name = name
        super().__init__(True)



class AMap():
    def __init__(self, a1: A, a2: A, gamma):
        self.a1 = a1
        self.a2 = a2
        self.gamma = gamma
    
    def _validate(self):
        # TODO: Run validations if the instance is correct
        pass

    def _eval(self):
        return element_pair(self.a1.element, self.a2.element)


class AMapLeft(AMap):
    # TODO: Check types
    def eval(self, variables: Dict):
        return self._eval(variables[self.a1.name])

    def _eval(self, variable_element: Element):
        return element_pair(variable_element, self.a2.element)


class AMapRight(AMap):
    # TODO: Check types
    def eval(self, variables: Dict):
        return self._eval(variables[self.a2.name])

    def _eval(self, variable_element: Element):
        return element_pair(self.a1.element, variable_element)


class AMapBoth(AMap):
    # TODO: Check types
    def eval(self, variables: Dict):
        return self._eval(variables[self.a1.name], variables[self.a2.name])

    def _eval(self, variable_element1: Element, variable_element2: Element):
        return element_pair(variable_element1, variable_element2)


class AMapNone(AMap):
    # TODO: Check types
    def eval(self, variables: Dict):
        return element_pair(self.a1.element, self.a2.element)



    
class B():
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __json__(self):
        return {'e1': self.e1, 'e2': self.e2}
    
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


class BT(B):
    pass


class BMap():
    def __init__(self, b1: B1, b2: B2):
        self.b1 = b1
        self.b2 = b2

    def eval(self):
        return extended_pair(b1, b2)


class ExplicitVariable():
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
            u = CRS['u2'] + B1(element_zero(G1), CRS['u1'].e1) # u1.e1 is p1
            return self.element * u
        
        return B1(element_zero(G1), self.element)

    def _iota2(self, CRS):
        if self.element.type == ZR:
            v = CRS['v2'] + B2(element_zero(G2), CRS['v1'].e1) # v1.e1 is p2
            return self.element * v
        
        return B2(element_zero(G2), self.element)

    def _randomize(self, CRS):
        if self.position == 1 or self.element.type == G1:
            return self._randomize1(CRS)
        elif self.position == 2 or self.element.type == G2:
            return self._randomize2(CRS)
        raise Exception('Position not set')

    def _randomize1(self, CRS):
        if self.element.type == ZR:
            r = element_random(ZR)
            return (r,), r * CRS['u1']
        r1, r2 = [element_random(ZR) for _ in range(2)]
        return (r1, r2), r1 * CRS['u1'] + r2 * CRS['u2']

    def _randomize2(self, CRS):
        if self.element.type == ZR:
            r = element_random(ZR)
            return (r,), r * CRS.v1
        r1, r2 = [element_random(ZR) for _ in range(2)]
        return (r1, r2), r1 * CRS['v1'] + r2 * CRS['v2']

    def commit(self, CRS):
        R, randomization = self._randomize(CRS)
        return R, Commit(self.name, self.iota(CRS) + randomization)


class Commit():
    def __init__(self, name: str, b: B):
        self.name = name
        self.b = b

class Equation():
    def __init__(self, name:str, a_maps: List[AMap], target:A, eq_type):
        self.name = name

        self.type = eq_type
        self.a_maps = a_maps
        self.target = target

    def check(self, variables: Dict):
        pass

    def prove(self, comms: Dict):
        pass

    def verify(self, comms: Dict, theta, pi):
        pass



class PPEquation(Equation):
    def __init__(self, name:str, a_maps: List[AMap], target:A):
        super().__init__(name, a_maps, target, EQUATION_TYPES['PPE'])
