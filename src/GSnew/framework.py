import numpy as np
from elements import (
    Element,
    ZpElement,
    G1Element, # pairing function as method on G1Element
    G2Element,
    GTElement,
    g1,
    g2,)
from utils import NamedArray, UnamedArray, random_zp

import json



def load_crs(filename, new=None):
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


class CRS():
    def __init__(self, u1, u2, v1, v2, trapdoor=None):
        self._u1 = u1
        self._u2 = u2
        self._v1 = v1
        self._v2 = v2
        
        global g1, g2
        g1 = u1[0]
        g2 = v1[0]
        
    def iota_1(self, x: G1Element):
        return UnamedArray([G1Element.zero(), x])
        
    def iota_prime_1(self, x: ZpElement):
        u = self.u[1] + UnamedArray([G1Element.zero(), g1])
        #u = self.u[1] + UnamedArray([G1Element.zero(), self.u[0][0]])
        return x * u
        
    def iota_2(self, y: G2Element):
        return UnamedArray([G2Element.zero(), y])
        
    def iota_prime_2(self, y: ZpElement):
        v = self.v[1] + UnamedArray([G2Element.zero(), g2])
        #v = self.v[1] + UnamedArray([G2Element.zero(), self.v[0][0]])
        return y * v
    
    def iota_t(self, t: GTElement):
        return UnamedArray([GTElement.zero(), GTElement.zero(), GTElement.zero(), t])
    
    def iota_t_hat(self, t: G2Element):
        u = self.u[1] + UnamedArray([G1Element.zero(), self.u[0][0]])
        return u.b_pair(self.iota_2(t))
    
    def iota_t_tilde(self, t: G1Element):
        v = self.v[1] + UnamedArray([G2Element.zero(), self.v[0][0]])
        return self.iota_1(t).b_pair(v)
    
    def iota_t_prime(self, t: ZpElement):
        u = self.u[1] + UnamedArray([G1Element.zero(), self.u[0][0]])
        v = self.v[1] + UnamedArray([G2Element.zero(), self.v[0][0]])
        return u.b_pair(t * v)
        #return (self.iota_prime_1(Element.zero(0))).b_pair(self.iota_prime_2(t))

    @property
    def u(self):
        return UnamedArray([self._u1, self._u2])

    @property
    def v(self):
        return UnamedArray([self._v1, self._v2])
    
    @property
    def u1(self):
        return UnamedArray([self._u1])
    
    @property
    def u2(self):
        return UnamedArray([self._u2])
    
    @property
    def v1(self):
        return UnamedArray([self._v1])
    
    @property
    def v2(self):
        return UnamedArray([self._v2])

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
        def to_json_array(array):
            return np.array([[e.to_json() for e in b] for b in array])
         
        return json.dumps({
            **self.c.__json__(),
            **self.c_prime.__json__(),
            **self.d.__json__(),
            **self.d_prime.__json__(),
            'pis': self.pis,
            'thetas': self.thetas
        }, cls=NamedArray.NamedArrayEncoder)
        
    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        c = NamedArray([(com['name'], [Element.from_json(com['value'][0]), Element.from_json(com['value'][1])]) for com in data['c']])
        c_prime = NamedArray([(com['name'], [Element.from_json(com['value'][0]), Element.from_json(com['value'][1])]) for com in data['c_prime']])
        d = NamedArray([(com['name'], [Element.from_json(com['value'][0]), Element.from_json(com['value'][1])]) for com in data['d']])
        d_prime = NamedArray([(com['name'], [Element.from_json(com['value'][0]), Element.from_json(com['value'][1])]) for com in data['d_prime']])

        breakpoint()
        pis = [np.array([[Element.from_json(e) for e in b] for b in pi]) for pi in data['pis']]
        thetas = [np.array([[Element.from_json(e) for e in b] for b in theta]) for theta in data['thetas']]

        return cls(c, c_prime, d, d_prime, pis, thetas)



def proof(crs: CRS, eqs: equations, X, Y, x, y):
    m = len(X)
    m_prime = len(x)
    n = len(Y)
    n_prime = len(y)
    
    R = np.array([[ZpElement.random() for _ in range(2)] for _ in range(m)]) # shape (m, 2) of Zp
    r = np.array([ZpElement.random() for _ in range(m_prime)]) # shape (m,) of Zp
    
    #breakpoint()
    c = X.iota_1(crs) + R@crs.u if len(X) > 0 else NamedArray([])

    c_prime = x.iota_prime_1(crs) + r@crs.u1 if len(x) > 0 else NamedArray([])


    S = np.array([[ZpElement.random() for _ in range(2)] for _ in range(n)]) # shape (m, 2) of Zp
    s = np.array([ZpElement.random() for _ in range(n_prime)]) # shape (m,) of Zp

    d = Y.iota_2(crs) + S@crs.v if len(Y) > 0 else NamedArray([])

    d_prime = y.iota_prime_2(crs) + s@crs.v1 if len(y) > 0 else NamedArray([])
    
    pis = []
    thetas = []

    for eq in eqs.ppe:
        A = eq.a
        B = eq.b
        Gamma = np.array(eq.Gamma)

        T = random_zp(2,2)
        if len(X) == 0:
            pi = np.array([[G2Element.zero(), G2Element.zero()], [G2Element.zero(), G2Element.zero()]])
            theta = S.T @ np.array(list(map(crs.iota_1, A)))
        elif len(Y) == 0:
            pi = R.T @ np.array(list(map(crs.iota_2, B)))
            theta = np.array([[G1Element.zero(), G1Element.zero()], [G1Element.zero(), G1Element.zero()]])
        else:
            pi = R.T @ np.array(list(map(crs.iota_2, B))) + R.T @ Gamma @ Y.iota_2(crs) + (R.T @ Gamma @ S - T.T) @ crs.v
            theta = S.T @ np.array(list(map(crs.iota_1, A))) + S.T @ Gamma.T @ X.iota_1(crs) + T @ crs.u
        
        pis.append(UnamedArray(pi))
        thetas.append(UnamedArray(theta))
        
    for eq in eqs.ms1:
        A = eq.A
        b = eq.b
        Gamma = eq.Gamma

        T = random_zp(1,2)
        if len(X) == 0:
            pi = np.array([[G2Element.zero(), G2Element.zero()]])
            theta = S.T @ np.array(list(map(crs.iota_1, A)))
        elif len(y) == 0:
            pi = R.T @ np.array(list(map(crs.iota_2, B)))
            theta = np.array([G1Element.zero(), G1Element.zero()])
        else:
            pi = R.T @ crs.iota_prime_2(b) + R.T @ Gamma @ crs.iota_prime_2(y) + (R.T @ Gamma @ s - T.T) @ crs.v1
            theta = s.T @ crs.iota_1(A) + s.T @ Gamma.T @ crs.iota_1(X) + T @ crs.u

        pis.append(UnamedArray(pi))
        thetas.append(UnamedArray(theta))
        
    for eq in eqs.ms2:
        a = eq.a
        B = eq.B
        Gamma = eq.Gamma

        T = random_zp(2,1)
        if len(x) == 0:
            pi = np.array([G2Element.zero(), G2Element.zero()])
            theta = S.T @ np.array(list(map(crs.iota_1, a)))
        elif len(Y) == 0:
            pi = r.T @ np.array(list(map(crs.iota_2, B)))
            theta = np.array([[G1Element.zero(), G1Element.zero()]])
        pi = r.T * crs.iota_2(B) + r.T * Gamma * crs.iota_2(Y) + (r.T * Gamma * S - T.T) * crs.v
        theta = S.T * crs.iota_prime_1(a) + S.T * Gamma.T * crs.iota_prime_1(x) + T * crs.u1

        pis.append(UnamedArray(pi))
        thetas.append(UnamedArray(theta))
        
    for eq in eqs.qe:
        a = eq.a
        b = eq.b
        Gamma = np.array(eq.Gamma)

        T = ZpElement.random()
        if len(x) == 0:
            pi = np.array([G2Element.zero(), G2Element.zero()])
            theta = s.T @ np.array(list(map(crs.iota_prime_1, a)))
        elif len(y) == 0:
            pi = r.T @ np.array(list(map(crs.iota_prime_2, b)))
            theta = np.array([G1Element.zero(), G1Element.zero()])
        else:
            pi = r.T @ crs.iota_prime_2(b) + r.T @ Gamma @ crs.iota_prime_2(y) + (r.T @ Gamma @ s - T) @ crs.v1
            theta = s.T @ crs.iota_prime_1(a) + s.T @ Gamma.T @ crs.iota_prime_1(x) + T @ crs.u1
        
        pis.append(UnamedArray(pi))
        thetas.append(UnamedArray(theta))
        
    return Proof(c, c_prime, d, d_prime, pis, thetas)
    


def verify(crs: CRS, eqs: equations, c, c_prime, d, d_prime, pis, thetas):

    for eq, pi, theta in zip(eqs, pis, thetas):
        a = UnamedArray(eq.a)
        b = UnamedArray(eq.b)
        Gamma = UnamedArray(eq.Gamma)
        t = eq.t
        
        if eq.etype == 3:
            lhs = (a.iota_1(crs)).b_pair(d) * c.b_pair(b.iota_2(crs)) * c.b_pair(Gamma @ d)
            breakpoint()
            rhs = crs.iota_t(t) * crs.u.b_pair(pi) * theta.b_pair(crs.v)
            breakpoint()
            if not np.all(lhs == rhs): return False
        
        elif eq.etype == 1:
            lhs = (a.iota_1(crs)).b_pair(d_prime) * c.b_pair(b.iota_prime_2(crs)) * c.b_pair(Gamma @ d_prime)
            rhs = crs.iota_t_tilde(t) * crs.u.b_pair(pi) * theta.b_pair(crs.v[0])
            if not np.all(lhs == rhs): return False
        elif eq.etype == 2:
            lhs = (a.iota_prime_1(crs)).b_pair(d) * c_prime.b_pair(b.iota_2(crs)) * c_prime.b_pair(Gamma @ d)
            rhs = crs.iota_t_hat(t) * crs.u[0].b_pair(pi) * theta.b_pair(crs.v)
            if not np.all(lhs == rhs): return False
        elif eq.etype == 0:
            breakpoint()
            lhs = (a.iota_prime_1(crs)).b_pair(d_prime) * c_prime.b_pair(b.iota_prime_2(crs)) * c_prime.b_pair(Gamma @ d_prime)
            rhs = crs.iota_t_prime(t) * crs.u[0].b_pair(pi) * theta.b_pair(crs.v[0])
            if not np.all(lhs == rhs): return False
    return True