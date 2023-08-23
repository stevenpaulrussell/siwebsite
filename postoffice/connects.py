
import time
import uuid

from saveget import saveget

def connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, text):
        cmd, requesting_from_tel, passkey_literal, passkey = [word.strip() for word in text.split(' ')]
        try:    
            requester = saveget.get_sender(requesting_from_tel)
            found_key, requester_to_tel = get_passkey(requesting_from_tel)     # Raises TypeError if no passkey
            assert(found_key == passkey)
            assert cmd == 'connect'
            assert passkey_literal == 'passkey'
            assert len(passkey) == 4
        except (ValueError, AssertionError, TypeError):
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        accepting_correspondence = saveget.get_correspondence(from_tel, to_tel)
        target_pobox_id = accepting_correspondence['pobox_id']
        target_name = accepting_correspondence['name_of_to_tel']
        requesting_correspondence = saveget.get_correspondence(requesting_from_tel, requester_to_tel)
        requesting_correspondence['pobox_id'] = target_pobox_id
        requesting_correspondence['name_of_to_tel'] = target_name
        requester['morsel'][requester_to_tel]['name_of_to_tel'] = target_name
        saveget.save_correspondence(requesting_from_tel, requester_to_tel, requesting_correspondence)
        saveget.update_sender_and_morsel(requester)
        #  -> Send message to both from_tels about the connection, the naming, and how to change.
        return f'Successfully connected {requesting_from_tel} to {target_name}'


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
    


    