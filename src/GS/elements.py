from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair,pairing
import numpy as np
from functools import reduce


def element_zero(group_type):
    '''
    if group_type == ZR:
        return ZpElement(group.init(group_type))
    if group_type == G1:
        return G1Element(group.init(group_type))
    if group_type == G2:
        return G2Element(group.init(group_type))
    if group_type == GT:
        return GTElement(group.init(group_type))
    '''
    return ELEMENT_DICT[group_type](group.init(group_type))

def element_pair(a, b):
    return GTElement(pair(a.group_element, b.group_element))

def extended_pair(x: np.ndarray, y:np.ndarray):
    '''
    x.shape == (2,1)
    y.shape == (1,2)
    '''
    assert x.shape == (2,1)
    assert y.shape == (1,2)

    return np.array([[element_pair(x[0][0], y[0][0]), element_pair(x[0][0], y[0][1])],
                     [element_pair(x[1][0], y[0][0]), element_pair(x[1][0], y[0][1])]])

def vector_element_pair(x: np.ndarray, y:np.ndarray):
    assert x.T.shape == y.shape

    return reduce(lambda e1,e2: e1+e2, element_pair(x[i][0], y[0][i]))

def vector_extended_pair(x: np.ndarray, y:np.ndarray):
    assert x.T.shape == y.shape

    return reduce(lambda e1,e2: e1+e2, extended_pair(x[i][0], y[0][i]))
     

class Element():
    """ Element is a wrapper of elements of Zp, G1, G2 & GT
    using additive notation

    """
    def __init__(self, group_element):
        self.group_element = group_element

    def __add__(self, other):
        raise NotImplemented

    def __mul__(self, other):
        raise NotImplemented

    def __pow__(self, other):
        raise NotImplemented

    def __eq__(self, other):
        return self.group_element == other.group_element

    def iota(self, target):
        raise NotImplemented
    
    def commit(self):
        raise NotImplemented

    def __repr__(self):
        return f"{self.group_element}"
    
    @property
    def type(self):
        """
        0 = Zp
        1 = G1
        2 = G2
        3 = GT
        """
        return self.group_element.type


class ZpElement(Element):
    def __init__(self, group_element, a_i=None):
        assert group_element.type == ZR
        self.a_i = a_i
        super().__init__(group_element)

    def __add__(self, other):
        if self.type != other.type:
            raise Exception
        return ZpElement(self.group_element + other.group_element)

    def __mul__(self, other):
        if other.type == ZR:
            return ZpElement(self.group_element * other.group_element)
        if other.type == G1:
            return G1Element(other.group_element ** self.group_element)
        if other.type == G2:
            return G2Element(other.group_element ** self.group_element)

    def iota(self, target):
        global W1, W2
        if target:
            # iota_t
            return extended_pair(W1, W2) ** self
        if self.a_i == 1:
            # iota_1
            return W1 ** self
        if self.a_i == 2:
            # iota_2
            return W2 ** self

    def to_commit(self):
        pass

    def commit(self):
        global U, U1, U2
        r = np.array([[group.random(ZR) for _ in range(2)]])
        return self.iota() + r*U


class G1Element(Element):
    def __init__(self, group_element):
        assert group_element.type == G1
        super().__init__(group_element)

    def __add__(self, other):
        if self.type != other.type:
            raise Exception
        return Element(self.group_element * other.group_element)

    def __mul__(self, other):
        raise Exception

    def iota(self, target):
        global W1, W2
        if target:
            # iota_t
            return np.array([[group_zero(GT), group_zero(GT)],
                             [element_pair(self, W2[0][0]), element_pair(self, W2[0][1])]])
        # iota_1
        return np.array([[group.init(self.type), self]]).T

    def commit(self):
        global U, U1, U2
        r = np.array([[group.random(ZR) for _ in range(2)]])
        return self.iota() + r*U


class G2Element(Element):
    def __init__(self, group_element):
        assert group_element.type == G2
        super().__init__(group_element)

    def __add__(self, other):
        if self.type != other.type:
            raise Exception
        return Element(self.group_element * other.group_element)

    def __mul__(self, other):
        raise Exception

    def iota(self, target):
        global W1, W2
        if target:
            # iota_t
            return np.array([[group_zero(GT), element_pair(W1[0][0], self)],
                             [group.zero(GT), element_pair(W1[1][0], self)]])
        # iota_2
        return np.array([[group.init(self.type), self]])
        
        
    def commit(self):
        global U, U1, U2
        r = np.array([[group.random(ZR) for _ in range(2)]])
        return self.iota() + r*U


class GTElement(Element):
    def __init__(self, group_element):
        assert group_element.type == GT
        super().__init__(group_element)

    def __add__(self, other):
        raise Exception

    def __mul__(self, other):
        raise Exception

    def __pow__(self, other):
        if other.type != ZR:
            raise Exception
        return Element(self.group_element ** other.group_element)

    def iota(self, target):
        global W1, W2
        if not target:
            raise Exception
        
        # Pairing Product Equation
        return np.array([[element_zero(GT), element_zero(GT)],
                         [element_zero(GT), self]])

    def commit(self):
        global U, U1, U2
        r = np.array([[group.random(ZR) for _ in range(2)]])
        return self.iota() + r*U

ELEMENT_DICT = {
    0: ZpElement,
    1: G1Element,
    2: G2Element,
    3: GTElement
}