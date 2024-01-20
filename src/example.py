from GS.proof import GS
from GS.equations import PPEquation, QEquation, MS1Equation, MS2Equation, Variable, Constant, Variable, AMapRight, AMapLeft, AMapBoth
from GS.elements import Element, ZpElement, G1Element, G2Element, group

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

proof = gs.prove([e2], {ev2.name: ev2})

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

print(f"QE (GS): {qv}")



# PPE with gamma example
a = G1Element.random()
b = G2Element.random()
z = ZpElement.random()

target = a.pair(b) ** z

l = Variable('a', a, 1)
r = Variable('b', b, 2)

t = Constant(target)

a_map = AMapBoth(l, r, z)
a_map._validate(3)
e = PPEquation('eqg', [a_map], t)

acom = l.commit(gs.CRS)
bcom = r.commit(gs.CRS)

p = e.prove({'a':acom, 'b':bcom}, {'a':l, 'b':r}, gs.CRS)
v = e.verify({'a':acom, 'b':bcom}, p[0], p[1], gs.CRS)

print(f"PPE gamma (GS): {v}")


# MS1 with gamma example
a = G1Element.random()
b = ZpElement.random()
z = ZpElement.random()

target = z * b * a

l = Variable('a', a, 1)
#r = Variable('b', b, 2)
r = Variable('b', ~b, 2) # Check false statement

t = Constant(target)

a_map = AMapBoth(l, r, z)
a_map._validate(1)
e = MS1Equation('eqg', [a_map], t)

acom = l.commit(gs.CRS)
bcom = r.commit(gs.CRS)

p = e.prove({'a':acom, 'b':bcom}, {'a':l, 'b':r}, gs.CRS)
v = e.verify({'a':acom, 'b':bcom}, p[0], p[1], gs.CRS)

print(f"MS1 gamma (GS): {v}")
