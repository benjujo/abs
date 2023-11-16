from GS.elements import *
from charm.schemes.pksig.pksig_bls04 import BLS01
from charm.toolbox.pairinggroup import PairingGroup, ZR, G1, G2, pair


group = PairingGroup('BN254')

bls = BLS01(group)

pk,sk = bls.keygen()

