from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair,pairing
import numpy as np
from functools import reduce

group = PairingGroup('BN254')

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

def element_random(group_type):
    return ELEMENT_DICT[group_type](group.random(group_type))

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
        return NotImplemented

    def __mul__(self, other):
        return NotImplemented

    def __pow__(self, other):
        return NotImplemented

    def __eq__(self, other):
        return self.group_element == other.group_element

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
    def __init__(self, group_element):
        assert group_element.type == ZR
        #self.a_i = a_i
        super().__init__(group_element)

    def __add__(self, other):
        if self.type != other.type:
            raise Exception
        return ZpElement(self.group_element + other.group_element)

    def __sub__(self, other):
        if self.type != other.type:
            raise Exception
        return ZpElement(self.group_element - other.group_element)

    def __mul__(self, other):
        if isinstance(other, ZpElement):
            return ZpElement(self.group_element * other.group_element)
        if isinstance(other, G1Element):
            return G1Element(other.group_element ** self.group_element)
        if isinstance(other, G2Element):
            return G2Element(other.group_element ** self.group_element)
        return NotImplemented


class G1Element(Element):
    def __init__(self, group_element):
        assert group_element.type == G1
        super().__init__(group_element)

    def __add__(self, other):
        if self.type != other.type:
            raise Exception
        return G1Element(self.group_element * other.group_element)

    def __sub__(self, other):
        if self.type != other.type:
            raise Exception
        return G1Element(self.group_element / other.group_element)

    def __mul__(self, other):
        if other.type != G2:
            raise Exception
        return GTElement(pair(self.group_element, other.group_element))


class G2Element(Element):
    def __init__(self, group_element):
        assert group_element.type == G2
        super().__init__(group_element)

    def __add__(self, other):
        if self.type != other.type:
            raise Exception
        return G2Element(self.group_element * other.group_element)

    def __sub__(self, other):
        if self.type != other.type:
            raise Exception
        return G2Element(self.group_element / other.group_element)

    def __mul__(self, other):
        raise Exception


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
        return GTElement(self.group_element ** other.group_element)



ELEMENT_DICT = {
    0: ZpElement,
    1: G1Element,
    2: G2Element,
    3: GTElement
}