import numpy as np
from elements import (
    Element,
    ZpElement,
    G1Element, # pairing function as method on G1Element
    G2Element,
    GTElement,
    g1,
    g2,)

import json

global json_defs
global crs
json_defs = None
crs = None

# TODO: filename should be 'defs.json'
def load_element(name, element_type, filename='bls_proof.json'):
    # Fortunately, charm doesn't need to know the element type
    with open(filename, 'r') as f:
        json_defs = json.load(f)
    
    if name == 'g1':
        return g1
    if name == 'g2':
        return g2
    element_string = json_defs[name]
    return Element.from_json(element_string)

def load_crs(new=None, filename='crs.json'):
    try:
        with open(filename, 'r') as f:
            crs = CRS.from_json(json.load(f))
    except FileNotFoundError:
        if new == 'sound':
            crs = CRS.new_sound()
        elif new == 'wi':
            crs = CRS.new_wi()
        else:
            raise Exception('CRS not valid')
    return crs


class G1ElementArray(np.ndarray):
    def __new__(cls, input_array):
        # Cast input_array to numpy array
        obj = np.asarray(input_array).view(cls)
        
        # Replace 0 with G2Element.zero()
        obj[obj == 0] = G1Element.zero()
        
        return obj


class G2ElementArray(np.ndarray):
    def __new__(cls, input_array):
        # Cast input_array to numpy array
        obj = np.asarray(input_array).view(cls)
        
        # Replace 0 with G2Element.zero()
        obj[obj == 0] = G2Element.zero()
        
        return obj


def random_zp(a,b):
    return np.array([[ZpElement.random() for _ in range(b)] for _ in range(a)])





class Equation():
    def __init__(self, a, b, Gamma, t, etype):
        self.a = a
        self.b = b
        self.t = t
        self.Gamma = Gamma
        self.etype = etype
        
        
class equations(list):
    def _by_equation_type(self, et):
        return list(item for item in self if item.etype == et)
    
    @property
    def ppe(self):
        return self._by_equation_type(3)
    
    @property
    def ms1(self):
        return self._by_equation_type(1)
    
    @property
    def ms2(self):
        return self._by_equation_type(2)
    
    @property
    def qe(self):
        return self._by_equation_type(0)


class Variable():
    def __init__(self, element, vtype=None):
        self.element = element
        self.vtype = vtype


class NamedArray(np.ndarray):
    def __new__(cls, input_data):
        # Extract the data, names, and element types from the input tuples
        names = [item[0] for item in input_data]
        data = [item[1] for item in input_data]
        
        # Create the ndarray
        obj = np.asarray(data).view(cls)
        # Store the names and element types as instance attributes
        obj.names = names
        return obj

    def __array_finalize__(self, obj):
        if obj is None: return
        self.names = getattr(obj, 'names', None)

    def __getitem__(self, key):
        if isinstance(key, str):
            index = self.names.index(key)
            return super().__getitem__(index)
        else:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            index = self.names.index(key)
            super().__setitem__(index, value)
        else:
            super().__setitem__(key, value)
    
class vars_array():
    def __init__(self, X, Y, x, y):
        self.X = NamedArray(X)
        self.Y = NamedArray(Y)
        self.x = NamedArray(x)
        self.y = NamedArray(y)



class CRS():
    def __init__(self, u1, u2, v1, v2, trapdoor=None):
        self.u1 = u1
        self.u2 = u2
        self.v1 = v1
        self.v2 = v2
        
    def iota_1(self, x: G1Element):
        return np.array([G1Element.zero(), x])
        
    def iota_prime_1(self, x: ZpElement):
        u = self.u2 + np.array([G1Element.zero(), g1])
        return x * u
        
    def iota_2(self, y: G2Element):
        return np.array([G2Element.zero(), y])
        
    def iota_prime_2(self, y: ZpElement):
        v = self.v2 + np.array([G2Element.zero(), g2])
        return y * v

    @property
    def u(self):
        return np.array([self.u1, self.u2])

    @property
    def v(self):
        return np.array([self.v1, self.v2])

    @staticmethod
    def from_json(json_string):
        u1 = np.array([G1Element.from_json(json_string['u1'][0]), G1Element.from_json(json_string['u1'][1])])
        u2 = np.array([G1Element.from_json(json_string['u2'][0]), G1Element.from_json(json_string['u2'][1])])
        v1 = np.array([G2Element.from_json(json_string['v1'][0]), G2Element.from_json(json_string['v1'][1])])
        v2 = np.array([G2Element.from_json(json_string['v2'][0]), G2Element.from_json(json_string['v2'][1])])
        return CRS(u1, u2, v1, v2)

    @staticmethod
    def new_sound(trapdoor=None):
        if  not trapdoor:
            trapdoor = {'alpha1': ZpElement.random(),
                        'alpha2': ZpElement.random(),
                        't1': ZpElement.random(),
                        't2': ZpElement.random()}
            
        alpha1 = trapdoor['alpha1']
        alpha2 = trapdoor['alpha2']
        t1 = trapdoor['t1']
        t2 = trapdoor['t2']

        u_1 = np.array([g1, alpha1 * g1])
        v_1 = np.array([g2, alpha2 * g2])
        u_2 = t1 * u_1
        v_2 = t2 * v_1
        
        return CRS(u_1, u_2, v_1, v_2, trapdoor=trapdoor)

    @staticmethod
    def new_wi(trapdoor=None):
        if  not trapdoor:
            trapdoor = {'alpha1': ZpElement.random(),
                        'alpha2': ZpElement.random(),
                        't1': ZpElement.random(),
                        't2': ZpElement.random()}
            
        alpha1 = trapdoor['alpha1']
        alpha2 = trapdoor['alpha2']
        t1 = trapdoor['t1']
        t2 = trapdoor['t2']

        u_1 = np.array([g1, alpha1 * g1])
        v_1 = np.array([g2, alpha2 * g2])
        u_2 = t1 * u_1 - np.array([G1Element.zero(), g1])
        v_2 = t2 * v_1 - np.array([G2Element.zero(), g2])
        
        return CRS(u_1, u_2, v_1, v_2, trapdoor=trapdoor)
        

class Proof():
    def __init__(self, c, c_prime, d, d_prime, pis, thetas):
        self.c = c
        self.c_prime = c_prime
        self.d = d
        self.d_prime = d_prime
        self.pis = pis
        self.thetas = thetas

    def to_json(self):
        return {
            'c': self.c,
            'c_prime': self.c_prime,
            'd': self.d,
            'd_prime': self.d_prime,
            'pis': self.pis,
            'thetas': self.thetas
        }



def proof(crs: CRS, eqs: equations, variables: vars_array):
    X = variables.X
    Y = variables.Y
    x = variables.x
    y = variables.y
    
    m = len(X)
    m_prime = len(x)
    n = len(Y)
    n_prime = len(y)
    
    R = np.array([[ZpElement.random() for _ in range(2)] for _ in range(m)]) # shape (m, 2) of Zp
    r = np.array([ZpElement.random() for _ in range(m_prime)]) # shape (m,) of Zp

    #breakpoint()
    c = np.array(list(map(crs.iota_1, X)), dtype=G1Element) + R@crs.u if len(X) > 0 else None
    c_prime = np.array(list(map(crs.iota_prime_1, x)), dtype=G1Element) + r@crs.u1 if len(x) > 0 else None

    S = np.array([[ZpElement.random() for _ in range(2)] for _ in range(n)]) # shape (m, 2) of Zp
    s = np.array([ZpElement.random() for _ in range(n_prime)]) # shape (m,) of Zp

    d = np.array(list(map(crs.iota_2, Y)), dtype=G2Element) + S@crs.v if len(Y) > 0 else None
    d_prime = np.array(list(map(crs.iota_prime_2, y)), dtype=G2Element) + s@crs.v1 if len(y) > 0 else None
    
    pis = []
    thetas = []

    for eq in eqs.ppe:
        A = eq.a
        B = eq.b
        Gamma = np.array(eq.Gamma)

        T = random_zp(2,2)
        if len(X) == 0:
            pi = np.array([G2Element.zero(), G2Element.zero()])
            theta = S.T @ np.array(list(map(crs.iota_1, A)))
        elif len(Y) == 0:
            pi = R.T @ np.array(list(map(crs.iota_2, B)))
            theta = np.array([G1Element.zero(), G1Element.zero()])
        else:
            pi = R.T @ np.array(list(map(crs.iota_2, B))) + R.T @ Gamma @ G2ElementArray(list(map(crs.iota_2 ,Y)), dtype=G2Element) + (R.T @ Gamma @ S - T.T) @ crs.v
            theta = S.T @ np.array(list(map(crs.iota_1, A))) + S.T @ Gamma.T @ np.array(list(map(crs.iota_1, X))) + T @ crs.u
        
        pis.append(pi)
        thetas.append(theta)
        
    for eq in eqs.ms1:
        A = eq.A
        b = eq.b
        Gamma = eq.Gamma

        T = random_zp(1,2)
        if len(X) == 0:
            pi = np.array([G2Element.zero(), G2Element.zero()])
            theta = S.T @ np.array(list(map(crs.iota_1, A)))
        elif len(y) == 0:
            pi = R.T @ np.array(list(map(crs.iota_2, B)))
            theta = np.array([G1Element.zero(), G1Element.zero()])
        else:
            pi = R.T @ crs.iota_prime_2(b) + R.T @ Gamma @ crs.iota_prime_2(y) + (R.T @ Gamma @ s - T.T) @ crs.v1
            theta = s.T @ crs.iota_1(A) + s.T @ Gamma.T @ crs.iota_1(X) + T @ crs.u

        pis.append(pi)
        thetas.append(theta)
        
    for eq in eqs.ms2:
        a = eq.a
        B = eq.B
        Gamma = eq.Gamma

        T = random_zp(2,1)
        pi = r.T * crs.iota_2(B) + r.T * Gamma * crs.iota_2(Y) + (r.T * Gamma * S - T.T) * crs.v
        theta = S.T * crs.iota_prime_1(a) + S.T * Gamma.T * crs.iota_prime_1(x) + T * crs.u1

        pis.append(pi)
        thetas.append(theta)
        
    for eq in eqs.qe:
        a = eq.a
        b = eq.b
        Gamma = eq.Gamma

        T = ZpElement.random()
        if len(x) == 0:
            pi = np.array([G2Element.zero()])
            theta = s.T @ np.array(list(map(crs.iota_prime_1, a)))
        elif len(y) == 0:
            pi = r.T @ np.array(list(map(crs.iota_prime_2, b)))
            theta = np.array([G1Element.zero()])
        else:
            pi = r.T @ crs.iota_prime_2(b) + r.T @ Gamma @ crs.iota_prime_2(y) + (r.T @ Gamma @ s - T) @ crs.v1
            theta = s.T @ crs.iota_prime_1(a) + s.T @ Gamma.T @ crs.iota_prime_1(x) + T @ crs.u1
        
        pis.append(pi)
        thetas.append(theta)
        
    return c, c_prime, d, d_prime, pis, thetas


def verify(crs: CRS, eqs: equations, proof: dict):
    c = proof['c']
    c_prime = proof['c_prime']
    d = proof['d']
    d_prime = proof['d_prime']
    pis = proof['pis']
    thetas = proof['thetas']

    for eq, pi, theta in zip(eqs, pis, thetas):
        if eq.etype == 3:
            if not np.allclose(crs.iota_1(eq.a) + crs.u @ theta, pi):
                return False
        elif eq.etype == 1:
            if not np.allclose(crs.iota_1(eq.A) + crs.u @ theta, pi):
                return False
        elif eq.etype == 2:
            if not np.allclose(crs.iota_2(eq.B) + crs.v @ theta, pi):
                return False
        elif eq.etype == 0:
            if not np.allclose(crs.iota_prime_1(eq.a) + crs.u1 @ theta, pi):
                return False
    return True