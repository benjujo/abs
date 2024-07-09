import numpy as np
from .elements import (
    ZpElement,
    G1Element, # pairing function as method on G1Element
    G2Element,
    GTElement,
    g1,
    g2)

def random_zp(a,b):
    return np.array([[ZpElement.random() for _ in range(b)] for _ in range(a)])


class Equation():
    def __init__(self):
        pass


class variables(list):
    def _by_element_type(self, et):
        # TODO: make it compilant to AST
        return list(item for item in self if item.type == et)
    
    @property
    def g1(self):
        return self._by_element_type(1)
    
    @property
    def g2(self):
        return self._by_element_type(2)
    
    @property
    def zpl(self):
        # TODO: fix this
        return self._by_element_type(0)
    
    @property
    def zpr(self):
        # TODO: fix this
        return self._by_element_type(0)


class equations(list):
    def _by_equation_type(self, et):
        return list(item for item in self if item.type == et)
    
    @property
    def ppe(self):
        return self._by_element_type(3)
    
    @property
    def ms1(self):
        return self._by_element_type(1)
    
    @property
    def ms2(self):
        return self._by_element_type(2)
    
    @property
    def qe(self):
        return self._by_element_type(0)

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
        

def proof(crs: CRS, eqs: equations, vars: variables):
    m = len(vars.g1)
    m_prime = len(vars.zpl)
    n = len(vars.g2)
    n_prime = len(vars.zpr)
    
    R = np.array([[ZpElement.random() for _ in range(2)] for _ in range(m)]) # shape (m, 2) of Zp
    r = np.array([ZpElement.random() for _ in range(m_prime)]) # shape (m,) of Zp

    c = np.array(map(crs.iota_1, vars.g1)) + R*crs.u # shape ()
    c_prime = np.array(map(crs.iota_prime_1, vars.zpl)) + r*crs.u1

    S = np.array([[ZpElement.random() for _ in range(2)] for _ in range(n)]) # shape (m, 2) of Zp
    s = np.array([ZpElement.random() for _ in range(n_prime)]) # shape (m,) of Zp

    d = np.array(map(crs.iota_2, vars.g2)) + S*crs.v # shape ()
    d_prime = np.array(map(crs.iota_prime_2, vars.zpr)) + s*crs.v1

    for eq in eqs.ppe:
        A = eq.A
        B = eq.B

        T = random_zp(2,2)
        pi = R.T * crs.iota_2()
