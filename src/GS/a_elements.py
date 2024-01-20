from .elements import Element, ZpElement, G1Element, G2Element, GTElement, ZR, G1, G2, GT
from .b_elements import B1, B2, BT, Commit


EQUATION_TYPES = {
    'PPE': 3,
    'MS1E': 1,
    'MS2E': 2,
    'QE': 0
}


class A():
    def __init__(self, element: Element):
        self.element = element

    def iota(self, CRS):
        try:
            position = self.position
            if position == 1:
                return self._iota1(CRS)
            elif position == 2:
                return self._iota2(CRS)
        except AttributeError:
            if self.element.type == G1:
                return self._iota1(CRS)
            elif self.element.type == G2:
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
            return self.iota(CRS).extended_pair(v)
        if eq_type == EQUATION_TYPES['MS2E']:
            u = CRS['u2'] + B1(G1Element.zero(), CRS['u1'].e1)
            return u.extended_pair(self.iota(CRS))
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
        super().__init__(element)

    def __json__(self):
        return {'element': self.element}

    @classmethod
    def from_json(cls, json):
        return cls(Element.from_json(json['element']))


class Variable(A):
    def __init__(self, name: str, element: Element, position: int = 0):
        self.name = name
        self.position = position
        super().__init__(element)

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
