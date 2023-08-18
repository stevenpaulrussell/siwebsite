
import time
import uuid

from saveget import saveget

def connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, text):
        lead_sender = saveget.get_sender(from_tel)
        cmd, joiner_from_tel, passkey_literal, passkey = [word.strip() for word in text.split(' ')]
        try:    
            joiner = saveget.get_sender(joiner_from_tel)
            found_key, joiner_to_tel = get_passkey(joiner_from_tel)     # Raises TypeError if no passkey
            assert(found_key == passkey)
            assert cmd == 'connect'
            assert passkey_literal == 'passkey'
            assert len(passkey) == 4
        except (ValueError, AssertionError, TypeError):
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        dest_correspondence = saveget.get_correspondence(lead_sender['from_tel'], to_tel)
        joiner_correspondence = saveget.get_correspondence(joiner['from_tel'], joiner_to_tel)
        joiner_correspondence['pobox_id'] = dest_correspondence['pobox_id']
        joiner_correspondence['name_of_to_tel'] = 'kith or kin'
        joiner['morsel'][joiner_to_tel]['name_of_to_tel'] = 'kith or kin'
        saveget.save_correspondence(joiner['from_tel'], joiner_to_tel, joiner_correspondence)
        saveget.update_sender_and_morsel(joiner)
        return f'Successfully connected {joiner["from_tel"]} to {dest_correspondence["name_of_to_tel"]}'


def get_passkey(from_tel):
    """Return both the passkey and the to_tel associated, to allow matching for security or for to_tel ident."""
    passkey_dictionary = saveget.get_passkey_dictionary(from_tel)
    if passkey_dictionary and time.time() < passkey_dictionary['expire']:
        return passkey_dictionary['passkey'], passkey_dictionary['to_tel']
    
def _set_passkey(from_tel, to_tel, duration=24):
    """Used only for test in this module"""
    expire = time.time() + duration*60*60
    passkey = str(uuid.uuid4())[0:4]
    current_key = dict(passkey=passkey, from_tel=from_tel, to_tel=to_tel, expire=expire)
    saveget.save_passkey_dictionary(current_key)
    


    