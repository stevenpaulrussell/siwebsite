
import time
import uuid
import os

from saveget import saveget

def connect_joining_sender_to_lead_sender_pobox(tel_id, svc_id, command_string):
    """Check the command integrity, change the requester boxlink, change the acceptor pobox and the requestor pobox if there is one."""
    try:
        requesting_tel_id, requester_svc_id = check_the_connect_command(command_string)
    except (ValueError, AssertionError, TypeError):
        if os.environ['TEST'] == 'True':
            raise
        return f'Sorry, there is some problem with, "{command_string}". Try "?" for help.'
    # This split to enable unit testing
    return _connect_joining_sender_to_lead_sender_pobox(tel_id, svc_id, requesting_tel_id, requester_svc_id)
    
def _connect_joining_sender_to_lead_sender_pobox(tel_id, svc_id, requesting_tel_id, requester_svc_id):
    # This split from the validity checking to enable unit testing
    requesting_boxlink = saveget.get_boxlink(requesting_tel_id, requester_svc_id)
    accepting_boxlink = saveget.get_boxlink(tel_id, svc_id)
    if requesting_boxlink['pobox_id']:
        delete_requester_from_former_pobox(requesting_tel_id, requesting_boxlink['pobox_id'])
    add_requester_to_accepting_pobox(requesting_tel_id, accepting_boxlink)
    update_the_requesting_morsel(requesting_tel_id, requester_svc_id, new_recipient=accepting_boxlink['recipient_moniker'])
    # Update the boxlink so requester points to acceptor pobox
    requesting_boxlink['recipient_moniker'] = accepting_boxlink['recipient_moniker']
    requesting_boxlink['pobox_id'] = accepting_boxlink['pobox_id']

    saveget.save_boxlink(requesting_boxlink)
    saveget.save_boxlink(accepting_boxlink)
    #  -> Send message to both tel_ids about the connection, the naming, and how to change.
    return f'Successfully connected {requesting_tel_id} to {tel_id}'
 
def check_the_connect_command(command_string):
    cmd, requesting_tel_id, passkey_literal, passkey = [word.strip() for word in command_string.split(' ')]
    found_key, requester_svc_id = get_passkey(requesting_tel_id)     # Raises TypeError if no passkey
    assert(found_key == passkey)
    assert cmd == 'connect'
    assert passkey_literal == 'passkey'
    assert len(passkey) == 4
    return requesting_tel_id, requester_svc_id
     

def update_the_requesting_morsel(requesting_tel_id, requester_svc_id, new_recipient):
    requester = saveget.get_sender(requesting_tel_id)
    requester['morsel'][requester_svc_id]['recipient_moniker'] = new_recipient
    saveget.update_sender_and_morsel(requester)     


def add_requester_to_accepting_pobox(requesting_tel_id, accepting_boxlink):
    """Add viewer_data format to the accepting pobox. """
    accepting_pobox = saveget.get_pobox(accepting_boxlink['pobox_id'])
    viewer_data = accepting_pobox['viewer_data']
    viewer_data[requesting_tel_id] = dict(
        card_id = None  # This and other parameters assigned when the first card is sent using the re-assigned boxlink
    )
    saveget.save_pobox(accepting_pobox)

    
def delete_requester_from_former_pobox(requesting_tel_id, requesters_former_pobox_id):
    """Delete viewer_data from requesting pobox if (there is one!), and then delete the pobox if viewer_data is empty"""
    requesters_former_pobox = saveget.get_pobox(requesters_former_pobox_id)
    try:
        viewer_data = requesters_former_pobox['viewer_data']
        assert(len(viewer_data)==1)
        assert(requesters_former_pobox['key_operator']==requesting_tel_id)
    except AssertionError:
        raise
    viewer_data.pop(requesting_tel_id)
    saveget.save_pobox(requesters_former_pobox)


def get_passkey(tel_id):
    """Return both the passkey and the svc_id associated, to allow matching for security or for svc_id ident."""
    passkey_dictionary = saveget.get_passkey_dictionary(tel_id)
    if passkey_dictionary and time.time() < passkey_dictionary['expire']:
        return passkey_dictionary['passkey'], passkey_dictionary['svc_id']
    
def _set_passkey(tel_id, svc_id, duration=24):
    """Used only for test in this module"""
    expire = time.time() + duration*60*60
    passkey = str(uuid.uuid4())[0:4]
    current_key = dict(passkey=passkey, tel_id=tel_id, svc_id=svc_id, expire=expire)
    saveget.save_passkey_dictionary(current_key)
    


    