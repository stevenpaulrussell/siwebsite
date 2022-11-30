"""
Does the postmaster work for sqs and also for browser-called commands.

def some_cmd(from_tel, to_tel, **msg):
    assert(msg['cmd'] == 'some_cmd')

"""


import time
import uuid

from . postcards import get_passkey_dictionary, save_passkey_dictionary

from filer import lines, exceptions


def get_passkey(from_tel, to_tel):
    current_key = get_passkey_dictionary(from_tel, to_tel)
    if current_key and time.time() < current_key['expire']:
        return current_key['passkey']
    

def set_passkey(from_tel, to_tel, duration=24):
    """Stores a short-lived 'passkey' for both security and easy id of a to_tell when adding a sender """
    expire = time.time() + duration*60*60
    passkey = str(uuid.uuid4())[0:4]
    current_key = dict(passkey=passkey, from_tel=from_tel, to_tel=to_tel, expire=expire)
    save_passkey_dictionary(current_key)
    return passkey

    


    