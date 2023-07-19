from absucl import *

absucl=ABSUCL()
A1=absucl.AASetup()
A2=absucl.AASetup()

absucl.add_vk("STUDENT@UCH", A1[1])
absucl.add_vk("RESIDENT@LF", A2[1])

usk = absucl.group.random()
o=objectToBytes(usk, absucl.group)
fsk=absucl.group.hash(o, ZR)

uid = absucl.group.init(0, 19361)

at1 = absucl.AttrKeyGen(uid, fsk, "STUDENT@UCH", A1[0])
at2 = absucl.AttrKeyGen(uid, fsk, "RESIDENT@LF", A1[0])
sk_id_a = {"STUDENT@UCH": at1, "RESIDENT@LF": at2}

policy_string="STUDENT@UCH and RESIDENT@LF"
m="wena wena"
recip=123
a_psdo = absucl.group.hash([policy_string,m,recip])
omega_hat = f"({policy_string}) or {a_psdo}"
M = absucl._span_program_generate(omega_hat)
v={1:1,2:1,3:0}

#spp = absucl._span_program_prove(v,M)
#dsp = absucl._ds1_ds2_prove(sk_id_a, v, 19361, usk, a_psdo, M)
#lit = absucl._lit(usk, 123, dsp["beta_sk"], dsp["beta_rho_sk"])
#responses = absucl._get_responses(absucl.group.hash("a"), dsp, 19361, usk, v, spp)


signature = absucl.Sign(m, policy_string, uid, usk, sk_id_a, v, recip)

Bc = absucl.Verify(signature, policy_string, "not wena", recip)


