import base64
from absucl import ABSUCL
absucl = ABSUCL()


f=lambda x: absucl.group.serialize(absucl.group.init(0,x))
check=lambda n: int.from_bytes(base64.decodebytes(f(n).split(b":")[1]), 'big')