from GS.elements import ZpElement, G1Element, G2Element
from typing import List, Tuple, Dict


class FBB():
    '''Full Boneh-Boyen signature scheme'''
    def __init__(self, CRS: Dict):
        self.g = CRS['u1'].e1
        self.h = CRS['v1'].e1

    def keygen(self) -> Tuple[List[ZpElement], List[G2Element]]:
        sk = [ZpElement.random() for _ in range(2)]
        vk = list(map(lambda x: x * self.h, sk))

        return (sk, vk)
    
    def sign(self, sk: List[ZpElement], m: ZpElement) -> Tuple[G1Element, ZpElement]:
        r = ZpElement.random()
        exp = sk[0] + r*sk[1] + m
        while exp == ZpElement.zero():
            r = ZpElement.random()
            exp = sk[0] + r*sk[1] + m
        sigma = ~exp * self.g

        return (sigma, r)
    
    def verify(self, vk: List[G2Element], m: ZpElement, signature: Tuple[G1Element, ZpElement]) -> bool:
        sigma = signature[0]
        r = signature[1]
        lhs = sigma.pair(vk[0] + r*vk[1] + m*self.h)
        rhs = self.g.pair(self.h)
        return lhs == rhs
