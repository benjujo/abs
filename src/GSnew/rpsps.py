from GS.elements import ZpElement, G1Element, G2Element
from typing import List, Tuple, Dict
from functools import reduce
import operator


class RPSPS():
    '''Ghadafi PSPS scheme
    ref: '''
    def __init__(self, CRS: Dict, N: int=1):
        self.g = CRS['u1'].e1
        self.h = CRS['v1'].e1
        self.N = N

    def keygen(self) -> Tuple[List[ZpElement], List[G2Element]]:
        sk = [ZpElement.random() for _ in range(self.N+2)] # sk = (x, y_1, ..., y_n, z)
        vk = list(map(lambda x: x * self.h, sk))

        return (sk, vk)
    
    def sign(self, sk: List[ZpElement], message: Tuple[Tuple[G1Element, G2Element], List[ZpElement]]) -> Tuple[G1Element, G1Element]:
        x,*y,z = sk

        U = message[0][0]
        V = message[0][1]
        m = message[1]

        r = ZpElement.random()

        R = r * self.g

        my_sum = sum([m[i] * y[i] for i in range(self.N)], ZpElement.zero())
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
        rhs = R.pair(V) * R.pair(X) * reduce(operator.mul, [R.pair(m[i] * Y[i]) for i in range(self.N)])

        return lhs == rhs
    
    @staticmethod
    def randomize(signature: Tuple[G1Element, G1Element]) -> Tuple[G1Element, G1Element]:
        R,S = signature

        r_prime = ZpElement.random()
        R_prime = r_prime * R
        S_prime = r_prime * S
        
        return (R_prime, S_prime)
