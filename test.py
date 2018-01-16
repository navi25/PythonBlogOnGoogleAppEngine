



import random
import string
import hashlib

x = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(5))



def make_pw_hash(name, pw):

    return "%s,%s" % (hashlib.md5(name + pw + x).hexdigest(),x)


f = make_pw_hash("navi", "sdfc")

print(f)
