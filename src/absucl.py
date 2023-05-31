from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from functools import reduce

from bbplus import BBPlusSig
from utils import msp2M


class ABSUCL():
    def __init__(self, g1=None, g2=None, h1=None, k1=None, k2=None, k3=None):
        # Setup algorithm
        self.group = PairingGroup('BN254')
        self.g1 = g1 if g1 != None else self.group.random(G1)
        self.g2 = g2 if g2 != None else self.group.random(G2)
        self.h1 = h1 if h1 != None else self.group.random(G1)

        self.k1 = k1 if k1 != None else self.group.random(G1)
        self.k2 = k2 if k2 != None else self.group.random(G2)
        self.k3 = k3 if k3 != None else self.group.random(G1)

        self.bbplus = BBPlusSig(g1, g2, h1)

    def AASetup(self):
        return self.bbplus.keygen()

    def UKeyGen(self):
        return self.group.random(ZR)

    def AttrKeyGen(self, id, fsk, a, sk_aa):
        attr = f"{a}_{id}"
        return self.bbplus.sign(sk_aa, attr, fsk)

    def _span_program_prove(self, v, M):
        alpha = len(M)
        theta = len(M[1])

        # Commitments of vector v
        beta_v = {}
        beta_t = {}
        t = {}
        V = {}

        for i in range(1, alpha+1):
            beta_v[i] = self.group.random(ZR)
            beta_t[i] = self.group.random(ZR)
            t[i] = self.group.random(ZR)

            V[i] = (self.g1 ** beta_v[i])*(self.k3 ** beta_t[i])
            vhat = (self.g1 ** v[i])*(self.k3 ** t[i])

        # Proofs of statement
        Lamda = {} # Misspelled in purpose
        lamda = {} # Misspelled in purpose

        for j in range(1, theta+1):
            Lamda[j] = reduce(lambda x,y: x*y, [self.k3 ** (t[i]*M[i][j]) for i in range(1, alpha+1)])
            lamda[j] = reduce(lambda x,y: x*y, [(self.k3**M[i][j])**beta_t[i] for i in range(1, alpha+1)])

        return {
            "commitments": (beta_v, beta_t, t, V),
            "proofs": (Lamda, lamda)
        }

    def _ds1_ds2_prove(self, sigmas, v):
        '''
        sigmas = {1:(sigma, r),...}
        '''
        alpha = len(sigmas)

        rho_v = {}
        rho_id = self.group.random(ZR)
        rho_r = {}
        rho_sk = self.group.random(ZR)
        beta_rho_sk = self.group.random(ZR)
        beta_id_rho_v = {}
        beta_r = {}
        beta_rho = {}
        beta_id = self.group.random(ZR)
        beta_rho_r = {}
        beta_rho_id = self.group.random(ZR)
        beta_cs = self.group.random(ZR)

        T = {}

        for i in range(1, alpha+1):
            rho_v[i] = self.group.random(ZR)
            rho_r[i] = self.group.random(ZR)
            beta_id_rho_v[i] = self.group.random(ZR)
            beta_r[i] = self.group.random(ZR)
            beta_rho[i] = self.group.random(ZR)
            beta_rho_r[i] = self.group.random(ZR)

            T[i] = sigmas[i]["sigma"]**v[i] * self.k1**rho_v[i]
            K[i] = 
        
