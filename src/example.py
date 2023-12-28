from GS.proof import GS
from GS.equations import PPEquation, QEquation, Variable, Constant, Variable, AMapRight, AMapLeft
from GS.elements import Element, ZpElement, G1Element, group

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
ev = Variable('v', pk, 2)
target = sigma.pair(pk_base)
t = Constant(target)

com = ev.commit(gs.CRS)

a_map = AMapRight(c, ev)
e = PPEquation('eq1', [a_map], t)

a_map._validate(1)
proof = e.prove({'v':com}, {'v':ev}, gs.CRS)

ver = e.verify({'v':com}, proof[0], proof[1], gs.CRS)


print(f"GS Verification (public key hiding): {ver}")

# GS verification of sigma
c2 = Constant(pk_base)
ev2 = Variable('v2', sigma, 1)
t2 = Constant(h.pair(pk))
com2 = ev2.commit(gs.CRS)

a2_map = AMapLeft(ev2, c2)
e2 = PPEquation('eq2', [a2_map], t2)

proof = gs.prove([e2], [ev2])

ver2 = gs.verify([e2], proof)

print(f"GS Verification (sigma hiding): {ver2}")

# QE example
a = ZpElement.random()
b = ZpElement.random()
c = a*b

print(f"QE: {a*b == c}")

r = Variable('a', a)
l = Constant(b)
t = Constant(c)

amap = AMapRight(l, r)
q = QEquation('q', [amap], t)
amap._validate(0)
com = r.commit(gs.CRS)
p = q.prove({'a':com}, {'a':r}, gs.CRS)
qv = q.verify({'a':com}, p[0], p[1], gs.CRS)