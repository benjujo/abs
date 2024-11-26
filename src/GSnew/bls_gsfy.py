from elements import ZpElement, G1Element, G2Element
from typing import Tuple

from gsfy import gsfy

debug = False 

class BLS():
    def __init__(self, g2=None):
        if g2 is None:
            self.g2 = G2Element.random()
        else:
            self.g2 = g2

    def keygen(self) -> Tuple[ZpElement, G2Element]:
        sk = ZpElement.random()
        vk = sk * self.g2

        return (sk, vk)
    
    def sign(self, sk: ZpElement, m: str) -> G1Element:
        h = G1Element.hash_from_string(m)

        return sk * h
    
    @gsfy
    def verify(self, vk: G2Element, m: str, signature: G1Element) -> bool:
        g2 = self.g2
        lhs = signature.pair(g2)
        rhs = G1Element.hash_from_string(m).pair(vk)
        GS_STRING = """
        variables:
            signature: G1

        constants:
            g2: G2
            rhs: GT

        equations:
            signature * g2 = rhs

        """
        return lhs == rhs
    
    


def main():
    m = "Wena wena"
    bls = BLS(G2Element.random())
    
    (sk, vk) = bls.keygen()
    
    sig = bls.sign(sk, m)
    
    if debug: print(f"Message: '{m}'")
    if debug: print(f"Signature: '{sig}'")     
    assert bls.verify(vk, m, sig), "Failure!!!"
    if debug: print('SUCCESS!!!')


if __name__ == "__main__":
    debug = True
    main()
