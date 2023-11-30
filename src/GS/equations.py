from elements import *
from typing import List, Dict


EQUATION_TYPES = {
    'PPE': 3,
    'MS1E': 1,
    'MS2E': 2,
    'QE': 0
}


class A():
    def __init__(self, element):
        self.element = element
    
    @property
    def type(self):
        return self.element.type


class A1(A):
    def __init__(self):
        super().__init__()
        pass


class A2(A):
    def __init__(self):
        super().__init__()
        pass


class AT(A):
    def __init__(self):
        super().__init__()
        pass


class AMap():
    def __init__(self, a1: A1, a2: A2, gamma):
        self.a1 = a1
        self.a2 = a2
        self.gamma = gamma
    
    def _validate(self):
        # TODO: Run validations if the instance is correct
        pass

    def _eval(self):
        return element_pair(self.a1.element, self.a2.element)

    def extract_variables(self):
        vars = {}
        if isinstance(self.a_1, Variable):
            vars.update({self.a_1.name: self.a_2})
        if isinstance(self.a_2, Variable):
            vars.update({self.a_2.name: self.a_2})
        return vars

    
class A():
    def __init__(self, **kwargs):
        name = kwargs.get('name')
        element = kwargs.get('element')

        if name:
            self.witness = True
            self._name = name
        elif element:
            self.witness = False
            self._element = element
        else:
            raise Exception
        
        @property
        def element(self):
            if self.witness:
                raise Exception
            return self._element
        
        @property
        def name(self):
            if not self.witness:
                raise Exception
            return self._name
    
    @property
    def type(self):
        return self.element.type


class A1(A):
    pass


class A2(A):
    pass


class AT(A):
    def __init__(self, **kwargs):
        if kwargs.get('name'):
            raise Exception
        super().__init__(**kwargs)


class AMap():
    def __init__(self, a1: A1, a2: A2, gamma):
        self.a1 = a1
        self.a2 = a2
        self.gamma = gamma

    
class B():
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2
    


class B1(B):
    def __add__(self, other):
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



    

class Equation():
    def __init__(self, name:str, a_maps: List[AMap], target:AT, eq_type):
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
    def __init__(self, name:str, a_maps: List[AMap], target:AT):
        super().__init__(name, a_maps, target, EQUATION_TYPES['PPE'])
