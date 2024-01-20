from GS.elements import ZpElement, G1Element, G2Element
from typing import Tuple, Dict


class WBB():
    '''Weak Boneh-Boyen signature scheme'''
    def __init__(self, CRS: Dict):
        self.g = CRS['u1'].e1
        self.h = CRS['v1'].e1

    def keygen(self) -> Tuple[ZpElement, G2Element]:
        sk = ZpElement.random()
        vk = sk * self.h

        return (sk, vk)
    
    def sign(self, sk: ZpElement, m: ZpElement) -> G1Element:
        if m == -sk:
            return None
        exp = sk + m
        sigma = ~exp * self.g

        return sigma
    
    def verify(self, vk: G2Element, m: ZpElement, signature: G1Element) -> bool:
        lhs = signature.pair(vk + m*self.h)
        rhs = self.g.pair(self.h)
        return lhs == rhs
