from equations import Equation, B1, B2
from elements import Element, element_random, element_zero, ZR, G1, G2

from typing import List, Dict

class GS():
    def __init__(self, binding=True):
        # TODO: Create CRS Setup
        alpha1 = element_random(ZR)
        t1 = element_random(ZR)

        p1 = element_random(G1)
        q1 = alpha1 * p1
        u1 = B1(p1, q1)
        u2 = t1 * u1

        alpha2 = element_random(ZR)
        t2 = element_random(ZR)

        p2 = element_random(G2)
        q2 = alpha2 * p2
        v1 = B2(p2, q2)
        v2 = t2 * v1

        if not binding:
            u2 -= B1(element_zero(G1), p1)
            v2 -= B2(element_zero(G2), p2)


        CRS = {'u1': u1, 'u2': u2, 'v1': v1, 'v2': v2}
        self.CRS = CRS
        self.trapdoor = {'alpha1': alpha1, 'alpha2': alpha2, 't1': t1, 't2': t2}

        

    def prove(self, equations: List[Equation], variables: Dict):
        # TODO: Check equations
        # for eq in equations:
        #     if not eq.check(variables):
        #         raise EquationNotValid
        
        comms = {k: v.commit for k,v in variables.items()}

        proofs_dict = {}
        thetas = {}
        pis = {}

        for eq in equations:
            theta, pi = eq.prove(comms)

            thetas[eq.name] = theta
            pis[eq.name] = pi
        
        return thetas, pis


    def verify(self, equations: List[Equation], thetas, pis, comms):
        for eq in equations:
            theta = thetas[eq.name]
            pi = pis[eq.name]
            if not eq.verify(comms, theta, pi):
                return False
        return True
