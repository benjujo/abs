from charm.toolbox.pairinggroup import PairingGroup,ZR,G1,G2,GT,pair,pairing
from charm.core.engine.util import objectToBytes, bytesToObject


group = PairingGroup('BN254')

def load_element(name, group_type):
    return ELEMENT_DICT[group_type].from_json(name)

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

    def __invert__(self):
        return ELEMENT_DICT[self.group_element.type](~self.group_element)

    def __neg__(self):
        return ELEMENT_DICT[self.group_element.type](-self.group_element)

    def pair(self, other):
        return NotImplemented

    def __eq__(self, other):
        return self.group_element == other.group_element

    def __repr__(self):
        return f"{group.serialize(self.group_element)}"

    def __json__(self):
        #return group.serialize(self.group_element).decode('utf-8')
        return self.to_bytes().decode('utf-8')

    def to_bytes(self):
        return objectToBytes(self.group_element, group)

    @classmethod
    def from_bytes(cls, bytes_element):
        return cls(bytesToObject(bytes_element, group))

    @staticmethod
    def zero(group_type):
        return ELEMENT_DICT[group_type](group.init(group_type))

    @staticmethod
    def random(group_type):
        return ELEMENT_DICT[group_type](group.random(group_type))

    @staticmethod
    def from_json(json_str):
        #bytes_element = json_str.encode('utf-8')
        #group_element = group.deserialize(bytes_element)
        group_element = bytesToObject(json_str, group)
        return ELEMENT_DICT[group_element.type](group_element)
        
    @staticmethod
    def hash_from_string(string: str, group_type: int):
        '''
        Returns hash representation of string
        '''
        return ELEMENT_DICT[group_type](group.hash(string, group_type))
    
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
        super().__init__(group_element)

    def __add__(self, other):
        if not isinstance(other, ZpElement):
            raise Exception('Not a Zp element')
        return ZpElement(self.group_element + other.group_element)

    def __sub__(self, other):
        if not isinstance(other, ZpElement):
            raise Exception('Not a Zp element')
        return ZpElement(self.group_element - other.group_element)

    def __mul__(self, other):
        if isinstance(other, ZpElement):
            return ZpElement(self.group_element * other.group_element)
        if isinstance(other, G1Element):
            return G1Element(other.group_element ** self.group_element)
        if isinstance(other, G2Element):
            return G2Element(other.group_element ** self.group_element)
        return NotImplemented
    
    @staticmethod
    def zero():
        return Element.zero(ZR)

    @staticmethod
    def random():
        return Element.random(ZR)

    @staticmethod
    def hash_from_string(string: str):
        return Element.hash_from_string(string, ZR)

    @staticmethod
    def init(num: int):
        return ZpElement(group.init(ZR, num))

    @staticmethod
    def from_str(string: str):
        number = int.from_bytes(string.encode('utf-8'), byteorder='big', signed=False)
        return ZpElement(group.init(ZR, number))

    def to_str(self):
        z = self.group_element
        return (z).to_bytes(math.ceil((z).bit_length() / 8), byteorder = 'big', signed=False).decode('utf-8')


class G1Element(Element):
    def __init__(self, group_element):
        assert group_element.type == G1
        super().__init__(group_element)

    def __add__(self, other):
        if not isinstance(other, G1Element):
            raise Exception('Not a G1 element')
        return G1Element(self.group_element * other.group_element)

    def __sub__(self, other):
        if not isinstance(other, G1Element):
            raise Exception('Not a G1 element')
        return G1Element(self.group_element / other.group_element)

    def pair(self, other):
        if not isinstance(other, G2Element):
            raise Exception('Not a G2 element')
        if str(self) == "b'1:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'":
            return GTElement.zero()
        return GTElement(pair(self.group_element, other.group_element))
    
    @staticmethod
    def zero():
        return Element.zero(G1)

    @staticmethod
    def random():
        return Element.random(G1)

    @classmethod
    def hash_from_string(cls, string: str):
        return super().hash_from_string(string, G1)


class G2Element(Element):
    def __init__(self, group_element):
        assert group_element.type == G2
        super().__init__(group_element)

    def __add__(self, other):
        if not isinstance(other, G2Element):
            raise Exception('Not a G2 element')
        return G2Element(self.group_element * other.group_element)

    def __sub__(self, other):
        if not isinstance(other, G2Element):
            raise Exception('Not a G2 element')
        return G2Element(self.group_element / other.group_element)
    
    @staticmethod
    def zero():
        return Element.zero(G2)

    @staticmethod
    def random():
        return Element.random(G2)

    @classmethod
    def hash_from_string(cls, string: str):
        return super().hash_from_string(string, G2)


class GTElement(Element):
    def __init__(self, group_element):
        assert group_element.type == GT
        super().__init__(group_element)

    def __mul__(self, other):
        if not isinstance(other, GTElement):
            raise Exception('Not a GT element')
        return GTElement(self.group_element * other.group_element)

    def __pow__(self, other):
        if not isinstance(other, ZpElement):
            raise Exception('Not a Zp element')
        return GTElement(self.group_element ** other.group_element)
    
    @staticmethod
    def zero():
        return Element.zero(GT)

    @staticmethod
    def random():
        return Element.random(GT)



ELEMENT_DICT = {
    0: ZpElement,
    1: G1Element,
    2: G2Element,
    3: GTElement
}

g1 = G1Element.random()
g2 = G2Element.random()
