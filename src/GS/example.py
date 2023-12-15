from proof import GS
from equations import PPEquation, ExplicitVariable, Constant, Variable, AMapRight, AMapLeft
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

# GS verification of public key
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


print(f"GS Verification (public key hiding): {lhs == rhs}")

# GS verification of sigma
v2 = Variable('v2')
c2 = Constant(pk_base)
ev2 = ExplicitVariable('v2', sigma, 1)
t2 = Constant(h.pair(pk))
com2 = ev2.commit(gs.CRS)

a2_map = AMapLeft(v2, c2)
e2 = PPEquation('eq2', [a2_map], t2)

a2_map._validate()
proof2 = e2.prove({'v2':com2}, {'v2':ev2}, gs.CRS)

theta2 = proof2[0]
pi2 = proof2[1]

lhs2 = com2.b.extended_pair(c2.iota(gs.CRS))

iotat2 = t2._iotat(gs.CRS, 3)
pi21 = gs.CRS['u1'].extended_pair(pi2[0])
pi22 = gs.CRS['u2'].extended_pair(pi2[1])
rhs2 = [iotat2[i] * pi21[i] * pi22[i] for i in range(4)]

print(f"GS Verification (sigma hiding): {lhs2 == rhs2}")
