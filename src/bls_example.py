# BLS signature example https://en.wikipedia.org/wiki/BLS_digital_signature
from GS.elements import ZpElement, G1Element, G2Element
from GS.equations import PPEquation
from GS.a_elements import Constant, Variable
from GS.a_maps import AMapLeft
from GS.proof import GS

# Setup
gs = GS.setup()
pk_base = gs.CRS['v1'].e1 # G2

# KeyGen
sk = ZpElement.random() # Zr
pk = sk * pk_base # G2

# Sign
message = 'wena wena'
h = G1Element.hash_from_string(message) # Hash to G1 group

sigma = sk * h # G1

# Classic verification
print(f"Verification: {sigma.pair(pk_base) == h.pair(pk)}")


# NIZK
c = Constant(pk_base)
v = Variable('v', sigma)
t = Constant(h.pair(pk))

a_map = AMapLeft(v, c)
e = PPEquation('e', [a_map], t)
e._validate()

#com = v.commit(gs.CRS)

proof = gs.prove([e], {v.name: v})

ver = gs.verify([e], proof)

print(f"GS Verification (sigma hiding): {ver}")