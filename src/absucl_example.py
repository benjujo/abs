from absucl import ABSUCL, Attribute, AttributeAuthority, User


absucl = ABSUCL.setup()
aa1 = AttributeAuthority.new_authority("UCH", absucl)
aa2 = AttributeAuthority.new_authority("LF", absucl)
aa3 = AttributeAuthority.new_authority("K", absucl)
u1 = User.new_user("19361", absucl)
attribute1, sk_ida1 = aa1.sign_attribute("STUDENT", u1.f)
attribute2, sk_ida2 = aa2.sign_attribute("RESIDENT", u1.f)

u2 = User.new_user("1234", absucl)
attribute3, sk_ida3 = aa3.sign_attribute("RESIDENT", u2.f)

absucl.add_vk_attr("STUDENT@UCH", aa1.vk)
absucl.add_vk_attr("RESIDENT@LF", aa2.vk)
absucl.add_vk_attr("RESIDENT@K", aa3.vk)

message = "Wena wena"
predicate = "STUDENT@UCH and RESIDENT@LF"

signature = absucl.sign(message, predicate, u1.sk, {"STUDENT@UCH":sk_ida1, "RESIDENT@LF":sk_ida2}, 4)

verify1 = absucl.verify(message, predicate, signature, 4)
verify2 = absucl.verify(message, predicate, signature, 3)
verify3 = absucl.verify("Mala mala", predicate, signature, 4)


print(verify1)
print(verify2)
print(verify3)

fake_signature1 = absucl.sign(message, predicate, u1.sk, {"STUDENT@UCH":sk_ida1, "RESIDENT@K":sk_ida2}, 4)
fake_signature2 = absucl.sign(message, predicate, u1.sk, {"STUDENT@UCH":sk_ida1, "RESIDENT@LF":sk_ida3}, 4)
fake_signature3 = absucl.sign(message, predicate, u1.sk, {"STUDENT@UCH":sk_ida1, "RESIDENT@K":sk_ida3}, 4)

verify_fake1 = absucl.verify(message, predicate, fake_signature1, 4)
verify_fake2 = absucl.verify(message, predicate, fake_signature2, 4)
verify_fake3 = absucl.verify(message, predicate, fake_signature3, 4)

print(verify_fake1)
print(verify_fake2)
print(verify_fake3)


link_signature1 = absucl.sign("Qué tal?", "STUDENT@UCH", u1.sk, {"STUDENT@UCH":sk_ida1}, 4)
link_signature2 = absucl.sign("Ya no soy el de antes", predicate, u1.sk, {"STUDENT@UCH":sk_ida1, "RESIDENT@LF":sk_ida2}, 5)

link_link1 = absucl.link(message, predicate, signature, "Qué tal?", "STUDENT@UCH", link_signature1, 4)
link_link2 = absucl.link(message, predicate, signature, "Ya no soy el de antes", predicate, link_signature2, 4)

print(link_link1)
print(link_link2)

