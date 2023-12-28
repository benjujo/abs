from .equations import Equation, B1, B2, Variable
from .elements import Element, ZpElement, G1Element, G2Element, GTElement, ZR, G1, G2

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


        CRS = {'u1': u1, 'u2': u2, 'v1': v1, 'v2': v2, 'u': [u1, u2], 'v': [v1, v2]}
        trapdoor = {'alpha1': alpha1, 'alpha2': alpha2, 't1': t1, 't2': t2}
        return cls(CRS, trapdoor)

    def prove(self, equations: List[Equation], variables: List[Variable]):
        vars = {v.name: v for v in variables}

        for eq in equations:
            if not eq.check(vars):
                raise EquationNotValid
        
        list_comms = [v.commit(self.CRS) for v in variables]
        comms = {c.name: c for c in list_comms}

        thetas = {}
        pis = {}

        for eq in equations:
            theta, pi = eq.prove(comms, vars, self.CRS)

            thetas[eq.name] = theta
            pis[eq.name] = pi
        
        proof = Proof(thetas, pis, comms)

        return proof

    def _verify(self, equations: List[Equation], thetas: Dict[str, List[Element]], pis: Dict[str, List[Element]], comms: Dict[str, Element], CRS):
        for eq in equations:
            eq_name = eq.name

            theta = thetas[eq_name]
            pi = pis[eq_name]

            if not eq.verify(comms, theta, pi, CRS):
                return False
        return True

    def verify(self, equations: List[Equation], proof: "Proof"):
        thetas = proof.thetas
        pis = proof.pis
        comms = proof.comms

        return self._verify(equations, thetas, pis, comms, self.CRS)

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


class Proof:
    def __init__(self, thetas: Dict[str, List[Element]], pis: Dict[str, List[Element]], comms: Dict[str, Element]):
        self.thetas = thetas
        self.pis = pis
        self.comms = comms

    def serialize(self):
        return json.dumps({
            'thetas': self.thetas,
            'pis': self.pis,
            'comms': self.comms
        }, default=json_serializer)

    @classmethod
    def from_json(cls, proof_json):
        proof_dict = json.loads(proof_json)
        thetas = proof_dict['thetas']
        pis = proof_dict['pis']
        comms = proof_dict['comms']

        return cls(thetas, pis, comms)