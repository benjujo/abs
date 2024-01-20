from .elements import Element, ZpElement, G1Element, G2Element, GTElement, G1, G2
from typing import Tuple


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


class Commit(B):
    def __init__(self, name: str, b: B, r: Tuple[ZpElement, ...]):
        self.name = name
        #self.b = b
        self.r = r
        e1 = b.e1
        e2 = b.e2
        super().__init__(e1, e2)

    @property
    def b(self):
        if self.e1.type == G1:
            return B1(self.e1, self.e2)
        elif self.e1.type == G2:
            return B2(self.e1, self.e2)
        raise Exception('Invalid type')

    def __json__(self):
        return {'name': self.name, 'b': self.b, 'b_type': type(self.b).__name__}

    @classmethod
    def from_json(cls, json):
        # TODO: dispatch to B1 & B2
        return cls(json['name'], B.from_json(json['b']), None)
