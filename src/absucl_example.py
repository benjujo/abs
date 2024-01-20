from absucl import ABSUCL, Attribute, AttributeAuthority, User


absucl = ABSUCL.setup()
aa1 = AttributeAuthority.new_authority("UCH", absucl)
aa2 = AttributeAuthority.new_authority("LF", absucl)
aa3 = AttributeAuthority.new_authority("K", absucl)
u1 = User.new_user("19361", absucl)
attribute1, sk_ida1 = aa1.sign_attribute("STUDENT", u1.f)
attribute2, sk_ida2 = aa2.sign_attribute("RESIDENT", u1.f)

u2 = User.new_user("1234", absucl)

absucl.add_vk_attr("STUDENT@UCH", aa1.vk)
absucl.add_vk_attr("RESIDENT@LF", aa2.vk)
absucl.add_vk_attr("RESIDENT@K", aa3.vk)

message = "Wena wena"
predicate = "STUDENT@UCH and RESIDENT@LF"

signature, eqs = absucl.sign(message, predicate, u1.sk, {"STUDENT@UCH":sk_ida1, "RESIDENT@LF":sk_ida2}, 4)

verify = absucl.gs.verify(eqs, signature)
print(verify)