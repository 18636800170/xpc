import random
from datetime import datetime

import requests

from web.models.code import Code

CODE_EXPIRE_SECONDS=60*10





def gen_code():
    return str(random.randint(100000, 999999))


def verify_code(phone, code):
    cm = Code.objects.filter(phone=phone, code=code).first()
    if not cm:
        print("1")
        return False
    delay=(datetime.now()-cm.created_at.replace(tzinfo=None)).total_seconds()
    print(delay)
    if delay > CODE_EXPIRE_SECONDS:
        print("2")
        return False
    return True

