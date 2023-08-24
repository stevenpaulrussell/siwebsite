
import time
import uuid

from saveget import saveget

def connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, command_string):
    """Check the command integrity, change the requester correspondence, change the acceptor pobox and the requestor pobox if there is one."""
    try:
        requesting_from_tel, requester_to_tel = check_the_connect_command(command_string)
    except (ValueError, AssertionError, TypeError):
        return f'Sorry, there is some problem with, "{command_string}". Try "?" for help.'
    requesting_correspondence = saveget.get_correspondence(requesting_from_tel, requester_to_tel)
    accepting_correspondence = saveget.get_correspondence(from_tel, to_tel)
    requesters_former_pobox_id = requesting_correspondence['pobox_id']    
    acceptors_pobox_id = accepting_correspondence['pobox_id'] 
    update_the_requesting_correspondence_and_morsel(from_tel, to_tel, requesting_from_tel, requester_to_tel)
    update_the_requesting_pobox(requesting_from_tel, requesters_former_pobox_id)
    update_the_accepting_pobox(requesting_from_tel, acceptors_pobox_id)
    #  -> Send message to both from_tels about the connection, the naming, and how to change.
    return f'Successfully connected {requesting_from_tel} to {target_name}'


def check_the_connect_command(command_string):
    cmd, requesting_from_tel, passkey_literal, passkey = [word.strip() for word in command_string.split(' ')]
    found_key, requester_to_tel = get_passkey(requesting_from_tel)     # Raises TypeError if no passkey
    assert(found_key == passkey)
    assert cmd == 'connect'
    assert passkey_literal == 'passkey'
    assert len(passkey) == 4
    return requesting_from_tel, requester_to_tel
     

def update_the_requesting_correspondence_and_morsel(from_tel, to_tel, requesting_from_tel, requester_to_tel):
    # -> change correspondence to act like an object, having its own save parameters from_tel and to_tel inside!!
    requesting_correspondence = saveget.get_correspondence(requesting_from_tel, requester_to_tel)
    accepting_correspondence = saveget.get_correspondence(from_tel, to_tel)
    target_pobox_id = accepting_correspondence['pobox_id']
    target_name = accepting_correspondence['name_of_to_tel']
    requesting_correspondence['pobox_id'] = target_pobox_id
    requesting_correspondence['name_of_to_tel'] = target_name
    saveget.save_correspondence(requesting_from_tel, requester_to_tel, requesting_correspondence)
    requester = saveget.get_sender(requesting_from_tel)
    requester['morsel'][requester_to_tel]['name_of_to_tel'] = target_name
    saveget.update_sender_and_morsel(requester)     # Update the morsel to reflect 


def update_the_accepting_pobox(requesting_from_tel, acceptors_pobox_id):
    """Add viewer_data format to the accepting pobox. """
    accepting_pobox = saveget.get_pobox(acceptors_pobox_id)
    viewer_data = accepting_pobox['viewer_data']
    viewer_data[requesting_from_tel] = dict(
        card_id = None  # This nd other parameters assigned when the first card is sent using the re-assigned correspondence
    )
    saveget.save_pobox(accepting_pobox)

    
def update_the_requesting_pobox(requesting_from_tel, requesters_former_pobox_id):
    """Delete viewer_data from requesting pobox, and then delete the pobox if viewer_data is empty"""
    try:
        requesters_former_pobox = saveget.get_pobox(requesters_former_pobox_id)
    except KeyError:  # No pobox, nothing to do!
        print('xxxxxxxxxxxxxx')
        return
    try:
        viewer_data = requesters_former_pobox['viewer_data']
        assert(len(viewer_data)==1)
        assert(requesters_former_pobox['key_operator']==requesting_from_tel)
    except AssertionError:
        raise
    
    print('UUUUUUUUUUUUUUUU')





    # This not done!






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
    


    