from equations import Equation, B1, B2, ExplicitVariable
from elements import Element, ZpElement, G1Element, G2Element, GTElement, ZR, G1, G2

from typing import List, Dict
import json

def json_serializer(obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    else:
        # For non-serializable objects, use the default JSON serialization
        return json.JSONEncoder().default(obj)

class GS():
    def __init__(self, CRS, trapdoor=None):
        self.CRS = CRS
        self.trapdoor = trapdoor

    @classmethod
    def setup(cls, binding=True):
        alpha1 = ZpElement.random()
        t1 = ZpElement.random()

        p1 = G1Element.random()
        q1 = alpha1 * p1
        u1 = B1(p1, q1)
        u2 = t1 * u1

        alpha2 = ZpElement.random()
        t2 = ZpElement.random()

        p2 = G2Element.random()
        q2 = alpha2 * p2
        v1 = B2(p2, q2)
        v2 = t2 * v1

        if not binding:
            u2 -= B1(G1Element.random(), p1)
            v2 -= B2(G2Element.random(), p2)


        CRS = {'u1': u1, 'u2': u2, 'v1': v1, 'v2': v2}
        trapdoor = {'alpha1': alpha1, 'alpha2': alpha2, 't1': t1, 't2': t2}
        return cls(CRS, trapdoor)

    def prove(self, equations: List[Equation], variables: List[ExplicitVariable]):
        vars = {v.name: v for v in variables}

        for eq in equations:
            if not eq.check(vars):
                raise EquationNotValid
        
        list_comms = [v.commit() for v in variables]
        comms = {c.name: c for c in list_comms}

        R = {}
        for c in comms:
            R[c.name] = c[0]

        thetas = {}
        pis = {}

        for eq in equations:
            theta, pi = eq.prove(comms, vars)

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

    def serialize(self):
        return json.dumps(self.CRS, default=json_serializer)

    @classmethod
    def deserialize(cls, gs_json):
        gs_dict = json.loads(gs_json)
        u1 = B1.from_json(gs_dict['u1'])
        u2 = B1.from_json(gs_dict['u2'])
        v1 = B2.from_json(gs_dict['v1'])
        v2 = B2.from_json(gs_dict['v2'])

        CRS = {'u1': u1, 'u2': u2, 'v1': v1, 'v2': v2}
        return cls(CRS)
