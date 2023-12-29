from .GS.elements import ZpElement, G1Element, G2Element
from typing import List, Tuple, Dict
from functools import reduce
import operator


N = 1


class PSPS():
    '''Ghadafi PSPS scheme
    ref: '''
    def __init__(self, CRS: Dict):
        self.g = CRS['u1'].e1
        self.h = CRS['v1'].e1

    def keygen(self) -> Tuple[List[ZpElement], List[G2Element]]:
        sk = [ZpElement.random() for _ in range(N+2)] # sk = (x, y_1, ..., y_n, z)
        vk = list(map(lambda x: x * self.h, sk))

        return (sk, vk)
    
    def sign(self, sk: List[ZpElement], message: Tuple[Tuple[G1Element, G2Element], List[ZpElement]]) -> Tuple[G1Element, G1Element]:
        x,*y,z = sk

        U = message[0][0]
        V = message[0][1]
        m = message[1]

        r = ZpElement.random()

        R = r * self.g

        my_sum = sum([y[i] * m[i] for i in range(N)], ZpElement.zero())
        S = ~z * (r*U + (r * (x + my_sum)) * self.g)

        return (R, S)
    
    def verify(self, vk: List[G2Element], message: Tuple[Tuple[G1Element, G2Element], List[ZpElement]], signature: Tuple[G1Element, G1Element]) -> bool:
        X,*Y,Z = vk

        U = message[0][0]
        V = message[0][1]
        m = message[1]

        R,S = signature

        if U.pair(self.h) != self.g.pair(V):
            return False
        
        lhs = S.pair(Z)
        rhs = R.pair(V) * R.pair(X) * reduce(operator.mul, [R.pair(m[i] * Y[i]) for i in range(N)])

        return lhs == rhs
    
    @staticmethod
    def randomize(signature: Tuple[G1Element, ZpElement]) -> bool:
        R,S = signature

        r_prime = ZpElement.random()
        R_prime = r_prime * R
        S_prime = r_prime * S
        
        return (R_prime, S_prime)
