from proof import GS
from equations import PPEquation, ExplicitVariable, Constant, Variable, AMapRight
from elements import Element, ZpElement, G1Element, group

# BLS signature example https://en.wikipedia.org/wiki/BLS_digital_signature

gs = GS.setup()
pk_base = gs.CRS['v1'].e1 # G2


h = G1Element.hash_from_string('wena wena') # Hash to G1 group
sk = ZpElement.random() # Zr
pk = sk * pk_base # G2

sigma = sk * h # G1

# Classic verification
print(f"Verification: {sigma.pair(pk_base) == h.pair(pk)}")

# GS verification
c = Constant(h)
v = Variable('v')
ev = ExplicitVariable('v', pk, 2)
target = sigma.pair(pk_base)
t = Constant(target)

com = ev.commit(gs.CRS)

a_map = AMapRight(c, v)
e = PPEquation('eq1', [a_map], t)

a_map._validate()
proof = e.prove({'v':com}, {'v':ev}, gs.CRS)

theta = proof[0]
pi = proof[1]

lhs = c.iota(gs.CRS).extended_pair(com.b)


iotat = t._iotat(gs.CRS, 3)
theta1 = theta[0].extended_pair(gs.CRS['v1'])
theta2 = theta[1].extended_pair(gs.CRS['v2'])
rhs = [iotat[i] * theta1[i] * theta2[i] for i in range(4)]


print(f"GS Verification: {lhs == rhs}")