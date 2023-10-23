from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.core.engine.util import objectToBytes
from charm.toolbox.msp import MSP
from functools import reduce

from bbplus import BBPlusSig
from bb import BBSig
from utils import msp2M, str2z, strattr2zattr, randomarray


class ABSUCL():
    def __init__(self, group=None, g1=None, g2=None, h1=None, k1=None, k2=None, k3=None):
        # Setup algorithm
        self.group = group if group != None else PairingGroup('BN254')
        self.g1 = g1 if g1 != None else self.group.random(G1)
        self.g2 = g2 if g2 != None else self.group.random(G2)
        self.h1 = h1 if h1 != None else self.group.random(G1)

        self.k1 = k1 if k1 != None else self.group.random(G1)
        self.k2 = k2 if k2 != None else self.group.random(G2)
        self.k3 = k3 if k3 != None else self.group.random(G1)

        self.bbplus = BBPlusSig(g1, g2, h1)

        self.bb = BBSig(g1, g2)
        self.cred = self.bb.keygen()

        self.vks = {}

    def serialize(self, compression=True):
        serialize_dict = {
            "g1": self.group.serialize(self.g1, compression),
            "g2": self.group.serialize(self.g2, compression),
            "h1": self.group.serialize(self.h1, compression),
            "k1": self.group.serialize(self.k1, compression),
            "k2": self.group.serialize(self.k2, compression),
            "k3": self.group.serialize(self.k3, compression),
        }
        return serialize_dict
    
    def add_vk(self, attribute, vk):
        self.vks[attribute] = vk

    def AASetup(self):
        return self.bbplus.keygen()

    def UKeyGen(self):
        return self.group.random(ZR)

    def AttrKeyGen(self, id, fsk, a, sk_aa):
        attr = f"{a}_{id}"
        return self.bbplus.sign(sk_aa, strattr2zattr(attr), fsk)

    def _span_program_generate(self, policy_string):
        msp = MSP(self.group)
        tree_policy = msp.createPolicy(policy_string)
        matrix = msp.convert_policy_to_msp(tree_policy)
        M = msp2M(matrix)
        return M

    def _span_program_prove(self, v, M):
        alpha = len(M)
        theta = len(M[1])-1 # M[n] also includes 'index' parameter

        # Commitments of vector v
        beta_v = {}
        beta_t = {}
        t = {}
        Vc = {}
        v_hat = {}

        for i in range(1, alpha+1):
            beta_v[i] = self.group.random(ZR)
            beta_t[i] = self.group.random(ZR)
            t[i] = self.group.random(ZR)

            Vc[i] = (self.g1 ** beta_v[i])*(self.k3 ** beta_t[i])
            v_hat[i] = (self.g1 ** v[i])*(self.k3 ** t[i])

        # Proofs of statement
        Lamda = {} # Misspelled in purpose
        lamda = {} # Misspelled in purpose

        for j in range(1, theta+1):
            Lamda[j] = reduce(lambda x,y: x*y, [self.k3 ** (t[i]*M[i][j]) for i in range(1, alpha+1)])
            lamda[j] = reduce(lambda x,y: x*y, [(self.k3**M[i][j])**beta_t[i] for i in range(1, alpha+1)])

        '''
        return {
            "commitments": (beta_v, beta_t, t, Vc),
            "proofs": (Lamda, lamda)
        }
        '''
        return {
            "beta_v": beta_v,
            "beta_t": beta_t,
            "t": t,
            "Vc": Vc,
            "v_hat": v_hat,

            "Lamda": Lamda,
            "lamda": lamda
        }

    def _ds1_ds2_prove(self, sk_id_A, v, uid, sk, a_psdo, M):
        '''
        sigmas = {1:(sigma, r),...}
        v = 
        Ys = {1:Y,...}
        '''
        #alpha = len(sk_id_A)
        alpha = len(M)
        theta = len(M[1])-1

        X = {}
        Y = {}
        for index in M:
            if index == alpha:
                X[index] = self.cred[1]['X']
                Y[index] = self.cred[1]['Y']
                continue
            vk = self.vks[M[index]['index']]
            X[index] = vk['X']
            Y[index] = vk['Y']

        #rho_v = randomarray(self.group, alpha)
        rho_v = {}
        rho_id = self.group.random(ZR)
        rho_r = {}
        rho_sk = self.group.random(ZR)
        beta_rho_sk = self.group.random(ZR)
        beta_id_rho_v = {}
        beta_rho_v = {}
        beta_r = {}
        beta_rho = {}
        beta_id = self.group.random(ZR)
        beta_rho_r = {}
        beta_rho_id = self.group.random(ZR)
        #beta_cs = self.group.random(ZR)
        beta_sk = self.group.random(ZR)
        rho = {}
        beta_r_rho_v = {}

        T = {}
        K = {}
        K_hat = {}

        r = {}

        for i in range(1, alpha+1):
            rho_v[i] = self.group.random(ZR)
            rho_r[i] = self.group.random(ZR)
            beta_rho_v[i] = self.group.random(ZR)
            beta_r[i] = self.group.random(ZR)
            beta_rho[i] = self.group.random(ZR)
            beta_rho_r[i] = self.group.random(ZR)
            beta_r_rho_v[i] = self.group.random(ZR)

            if i < alpha:
                beta_id_rho_v[i] = self.group.random(ZR)

            # Test this
            try:
                r[i] = sk_id_A[M[i]['index']]["r"]
                T[i] = sk_id_A[M[i]['index']]["sigma"]**v[i] * self.k1**rho_v[i]
                K[i] = Y[i]**r[i] * self.k2**rho_r[i]
            except KeyError:
                r[i] = self.group.random(ZR)
                T[i] = self.group.random(G1)**v[i] * self.k1**rho_v[i]
                K[i] = Y[i]**r[i] * self.k2**rho_r[i]

            K_hat[i] = Y[i]**beta_r[i] * self.k2**beta_rho_r[i]

            rho[i] = rho_r[i] + rho_id if i<alpha else rho_r[i]

        Z = self.h1**sk * self.k1**rho_sk
        U = self.g2**uid * self.k2**rho_id

        Z_hat = self.h1**beta_sk * self.k1**beta_rho_sk
        U_hat = self.g2**beta_id * self.k2**beta_rho_id
        print(f"beta_id: {beta_id}")
        print(f"beta_rho_id: {beta_rho_id}")
        print(f"rho_id: {rho_id}")

        print(f"U_hat: {U_hat}")
        print(f"U_hat_ser: {self.group.serialize(U_hat)}")
        #print(f"Z_hat: {Z_hat}")
        #print(f"K_hat: {K_hat}")

        # Simplification
        X_prima = {}
        Y_prima = {}
        R = self.group.pair_prod(self.k1, self.g2)
        T_prima = {}
        D_prima = self.group.pair_prod(self.k1, self.g2**a_psdo)

        for i in range(1, alpha+1):
            X_prima[i] = self.group.pair_prod(self.k1, X[i]*self.g2**(str2z(M[i]['index'])*(2**32)))
            Y_prima[i] = self.group.pair_prod(self.k1, Y[i])
            T_prima[i] = self.group.pair_prod(T[i], self.k2)

        # Knowledge of Exponents
        Xc_prima = {}
        Yc_prima = {}
        Tc_prima = {}
        Rc = {}
        Dc_alpha = {}
        Pc = {}
        Bc = {}

        for i in range(1, alpha+1):
            Xc_prima[i] = {}
            Yc_prima[i] = {}
            Tc_prima[i] = {}
            for j in range(1, theta+1):
                Xc_prima[i][j] = (X_prima[i]**M[i][j])**beta_rho_v[i]
                Yc_prima[i][j] = (Y_prima[i]**M[i][j])**beta_r_rho_v[i]
                Tc_prima[i][j] = (T_prima[i]**M[i][j])**beta_rho[i]

        for i in range(1, alpha):
            Rc[i] = {}
            for j in range(1, theta+1):
                Rc[i][j] = (R**M[i][j])**beta_id_rho_v[i]

        for j in range(1, theta+1):
            Dc_alpha[j] = (D_prima**M[alpha][j])**beta_rho_v[alpha]
            Pc[j] = Xc_prima[alpha][j]*Yc_prima[alpha][j]*Tc_prima[alpha][j]*Dc_alpha[j]
            Bc[j] = Pc[j] *\
                 reduce(lambda x,y: x*y, [Xc_prima[i][j]*Yc_prima[i][j]*Rc[i][j]*Tc_prima[i][j] for i in range(1, alpha)])
        print("===")
        #print(Bc)

        for j in range(1, theta+1):
            print(f"Bc_{j}: {self.group.serialize(Bc[j])}")

        return {
            "rho_v": rho_v,
            "rho_id": rho_id,
            "rho_r": rho_r, 
            "rho_sk": rho_sk,
            "beta_rho_sk": beta_rho_sk,
            "beta_id_rho_v": beta_id_rho_v,
            "beta_rho_v": beta_rho_v,
            "beta_r": beta_r,
            "beta_rho": beta_rho,
            "beta_id": beta_id,
            "beta_rho_r": beta_rho_r,
            "beta_rho_id": beta_rho_id,
            "beta_sk": beta_sk,
            "rho": rho,
            "beta_r_rho_v": beta_r_rho_v,

            "T": T,
            "K": K,
            "K_hat": K_hat,
            "Z": Z,
            "U": U,
            "Z_hat": Z_hat,
            "U_hat": U_hat,

            "Bc": Bc,

            "r":r
        }
    
    def _lit(self, sk, recip, beta_sk, beta_rho_sk):
        clean_recip = objectToBytes(recip, self.group)
        hashed = self.group.hash(clean_recip, G1)
        Nc = hashed**beta_sk
        Lc = (self.h1/hashed)**beta_sk * self.k1**beta_rho_sk
        sigma_ucl = hashed**sk

        return {
            "Nc": Nc,
            "Lc": Lc,
            "sigma_ucl": sigma_ucl
        }

    def _get_challenge(self, value_list):
        concated = reduce(lambda x,y:x+y, [objectToBytes(obj, self.group) for obj in value_list])
        #c = self.group.hash(concated, ZR)
        c = self.group.hash("a", ZR)

        return c

    def _get_responses(self, c, dss_proof, uid, sk, v, span_program_proof):
        alpha = len(v)

        r = dss_proof["r"]

        t = span_program_proof["t"]
        beta_t = span_program_proof["beta_t"]
        beta_v = span_program_proof["beta_v"]

        beta_id = dss_proof["beta_id"]
        beta_sk = dss_proof["beta_sk"]
        beta_rho_sk = dss_proof["beta_rho_sk"]
        rho_sk = dss_proof["rho_sk"]
        beta_rho_id = dss_proof["beta_rho_id"]
        rho_id = dss_proof["rho_id"]
        #beta_v = beta_rho_dict["beta_v"]
        #beta_t = beta_rho_dict["beta_t"]
        beta_rho_v = dss_proof["beta_rho_v"]
        rho_v = dss_proof["rho_v"]
        beta_r_rho_v = dss_proof["beta_r_rho_v"]
        beta_rho = dss_proof["beta_rho"]
        rho = dss_proof["rho"]
        beta_rho_r = dss_proof["beta_rho_r"]
        rho_r = dss_proof["rho_r"]
        beta_r = dss_proof["beta_r"]
        beta_id_rho_v = dss_proof["beta_id_rho_v"]


        s_id = beta_id + c*uid
        s_sk = beta_sk + c*sk
        s_rho_sk = beta_rho_sk + c*rho_sk
        s_rho_id = beta_rho_id + c*rho_id

        print(f"s_id: {s_id}")
        print(f"c: {c}")
        print(f"uid: {uid}")
        print(f"s_rho_id: {s_rho_id}")

        s_v = {}
        s_t = {}
        s_rho_v = {}
        s_r_rho_v = {}
        s_rho = {}
        s_r = {}
        s_rho_r = {}
        s_id_rho_v = {}

        for i in range(1, alpha+1):
            s_v[i] = beta_v[i] + c*v[i]
            s_t[i] = beta_t[i] + c*t[i]

            s_rho_v[i] = beta_rho_v[i] + c*rho_v[i]
            s_r_rho_v[i] = beta_r_rho_v[i] + c*(r[i]*rho_v[i])
            s_rho[i] = beta_rho[i] + c*rho[i]
            s_r[i] = beta_r[i] + c*r[i]
            s_rho_r[i] = beta_rho_r[i] + c*rho_r[i]

            if i < alpha:
                s_id_rho_v[i] = beta_id_rho_v[i] + c*(uid*rho_v[i])

        return {
            "s_v": s_v,
            "s_t": s_t,
            "s_id": s_id,
            "s_sk": s_sk,
            "s_rho_sk": s_rho_sk,
            "s_rho_id": s_rho_id,

            "s_rho_v": s_rho_v,
            "s_r_rho_v": s_r_rho_v,
            "s_rho": s_rho,
            "s_r": s_r,
            "s_rho_r": s_rho_r,

            "s_id_rho_v": s_id_rho_v
        }

            
    def Sign(self, m, policy_string, uid, sk_id, sk_id_A, v, recip):
        '''
        sk_id_a: {'attr@loc':(sigma, r)}

        '''
        #uid = self.group.init(ZR, uid)

        a_psdo = self.group.hash([policy_string,m,recip])
        omega_hat = f"({policy_string}) or {a_psdo}"
        M = self._span_program_generate(omega_hat)
        alpha = len(M)
        span_program_proof = self._span_program_prove(v, M)

        Lamda = span_program_proof["Lamda"]

        ds_proves = self._ds1_ds2_prove(sk_id_A, v, uid, sk_id, a_psdo, M)

        lit_proof = self._lit(sk_id, recip, ds_proves["beta_sk"], ds_proves["beta_rho_sk"])

        c = self._get_challenge(["a"])

        Sigma = self._get_responses(c, ds_proves, uid, sk_id, v, span_program_proof)

        absucl_signature = {
            "Sigma": Sigma,
            "c": c,
            "Lamda": Lamda,
            "v_hat": span_program_proof["v_hat"],
            "T": ds_proves["T"],
            "K": ds_proves["K"],
            "U": ds_proves["U"],
            "Z": ds_proves["Z"],
            "sigma_ucl": lit_proof["sigma_ucl"]
        }

        return absucl_signature

    def Verify(self, signature, policy_string, m, recip):
        '''
        Omited vk_a
        '''
        a_psdo = self.group.hash([policy_string,m,recip])
        omega_hat = f"({policy_string}) or {a_psdo}"
        M = self._span_program_generate(omega_hat)
        alpha = len(M)
        theta = len(M[1])-1

        X = {}
        Y = {}
        for index in M:
            if index == alpha:
                X[index] = self.cred[1]['X']
                Y[index] = self.cred[1]['Y']
                continue
            vk = self.vks[M[index]['index']]
            X[index] = vk['X']
            Y[index] = vk['Y']

        T = signature["T"]
        K = signature["K"]
        U = signature["U"]
        Z = signature["Z"]
        v_hat = signature["v_hat"]
        Lamda = signature["Lamda"]
        Sigma = signature["Sigma"]

        c = signature["c"]

        Delta = {}
        E = {}

        Sc = {}
        K_hat = {}

        lamda = {}

        for j in range(1, theta+1):
            Delta[j] = self.group.pair_prod(T[alpha],
                                            (X[alpha]*K[alpha]*(self.g2**a_psdo))**M[alpha][j])
            
            '''
            E[j] = Delta[j] * reduce(lambda x,y: x*y, [self.group.pair_prod(T[i],
                                                                            (X[i]*K[i]*U)**M[i][j]) for i in range(1, alpha)])
            if j == 1:
                E[j] = E[j] / (self.group.pair_prod(self.g1, self.g2) * self.group.pair_prod(Z, self.g2))
            '''
            if j == 1:
                E[j] = Delta[j] * reduce(lambda x,y: x*y, [self.group.pair_prod(T[i],
                                                                                (X[i]*K[i]*U)**M[i][j])/(self.group.pair_prod(self.g1, self.g2) * self.group.pair_prod(Z, self.g2)) for i in range(1, alpha)])
            else:
                E[j] = Delta[j] * reduce(lambda x,y: x*y, [self.group.pair_prod(T[i],
                                                                                (X[i]*K[i]*U)**M[i][j]) for i in range(1, alpha)])


            
        U_hat = self.g2**Sigma["s_id"] * self.k2**Sigma["s_rho_id"] * U**-c
        Z_hat = self.h1**Sigma["s_sk"] * self.k1**Sigma["s_rho_sk"] * Z**-c

        print(f"U_hat: {U_hat}")
        print(f"U_hat_ser: {self.group.serialize(U_hat)}")
        #print(f"Z_hat: {Z_hat}")

        for i in range(1, alpha+1):
            Sc[i] = self.g1**Sigma["s_v"][i] * self.k3**Sigma["s_t"][i] * v_hat[i]**-c
            K_hat[i] = Y[i]**Sigma["s_r"][i] * self.k2**Sigma["s_rho_r"][i] * K[i]**-c
        #print(f"K_hat: {K_hat}")

        # Simplification
        X_prima = {}
        Y_prima = {}
        R = self.group.pair_prod(self.k1, self.g2)
        T_prima = {}
        D_prima = self.group.pair_prod(self.k1, self.g2**a_psdo)

        Pc = {}
        Bc = {}

        for i in range(1, alpha+1):
            X_prima[i] = self.group.pair_prod(self.k1, X[i]*self.g2**(str2z(M[i]['index'])*(2**32)))
            Y_prima[i] = self.group.pair_prod(self.k1, Y[i])
            T_prima[i] = self.group.pair_prod(T[i], self.k2)
        
        for j in range(1, theta+1):
            lamda[j] = Lamda[j]**-c * reduce(lambda x,y: x*y, [(self.k3**M[i][j])**Sigma["s_t"][i] for i in range(1, alpha+1)])
            Pc[j] = (X_prima[alpha]**M[alpha][j])**Sigma["s_rho_v"][alpha] *\
                    (Y_prima[alpha]**M[alpha][j])**Sigma["s_r_rho_v"][alpha] *\
                    (T_prima[alpha]**M[alpha][j])**Sigma["s_rho"][alpha] *\
                    (D_prima**M[alpha][j])**Sigma["s_rho_v"][alpha]
            Bc[j] = E[j]**-c *\
                    Pc[j] *\
                    reduce(lambda x,y: x*y,
                           [(X_prima[i]**M[i][j])**Sigma["s_rho_v"][i] *\
                            (Y_prima[i]**M[i][j])**Sigma["s_r_rho_v"][i] *\
                            (R**M[i][j])**Sigma["s_id_rho_v"][i] *\
                            (T_prima[i]**M[i][j])**Sigma["s_rho"][i] for i in range(1, alpha)])
        print("----")
        #print(Bc)
        return Bc
        

