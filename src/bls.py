from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, GT, pair
from charm.toolbox.PKSig import PKSig


debug = True
class BLSSig():
    """
    >>> group = PairingGroup('BN254')
    >>> n = 3    # how manu users are in the group
    >>> user = 1 # which user's key we will sign a message with
    >>> shortSig = ShortSig(group)
    >>> (global_public_key, global_master_secret_key, user_secret_keys) = shortSig.keygen(n)
    >>> msg = 'Hello World this is a message!'
    >>> signature = shortSig.sign(global_public_key, user_secret_keys[user], msg)
    >>> shortSig.verify(global_public_key, msg, signature)
    True
    """
    def __init__(self, g1=None, g2=None, h1=None):
        #self.group = group
        self.group = PairingGroup('BN254')
        #global group
        #group = groupObj
        self.g1 = g1 if g1 != None else self.group.random(G1)
        self.g2 = g2 if g2 != None else self.group.random(G2)
        self.h1 = h1 if h1 != None else self.group.random(G1)
        self.H = h # h = Hash(pairingElement=self.group)

        
    def keygen(self):
        sk = {'x': self.group.random(ZR),
              'y': self.group.random(ZR)}
        vk = {'X': self.g2**sk['x'],
              'Y': self.g2**sk['y']}

        return (sk, vk)
    
    def sign(self, sk, m, fsk):
        r = self.group.random(ZR)
        exp = sk['x'] + r*sk['y'] + m
        while exp == 0:
            r = self.group.random(ZR)
            exp = sk['x'] + r*sk['y'] + m
        sigma = (self.g1*fsk)**(1/exp)

        return {'sigma': sigma, 'r': r}
    
    def verify(self, pk, m, sig):
        v1 = pair(sig['sigma'], pk['X'] * (pk['Y']**sig['r']) * (self.g2**m))
        v2 = pair(self.g1, self.g2)
        return v1 == v2
    