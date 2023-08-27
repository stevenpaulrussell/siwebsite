
import time
import uuid

from saveget import saveget

def connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, command_string):
    """Check the command integrity, change the requester correspondence, change the acceptor pobox and the requestor pobox if there is one."""
    try:
        requesting_from_tel, requester_to_tel = check_the_connect_command(command_string)
    except (ValueError, AssertionError, TypeError):
        return f'Sorry, there is some problem with, "{command_string}". Try "?" for help.'
    # This split to enable unit testing
    return _connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, requesting_from_tel, requester_to_tel)
    
def _connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, requesting_from_tel, requester_to_tel):
    # This split from the validity checking to enable unit testing
    requesting_correspondence = saveget.get_correspondence(requesting_from_tel, requester_to_tel)
    accepting_correspondence = saveget.get_correspondence(from_tel, to_tel)
    delete_requester_from_former_pobox(requesting_from_tel, requesting_correspondence['pobox_id'])
    add_requester_to_accepting_pobox(requesting_from_tel, accepting_correspondence)
    update_the_requesting_morsel(requesting_from_tel, requester_to_tel, new_recipient=accepting_correspondence['name_of_to_tel'])
    # Update the correspondence so requester points to acceptor pobox
    requesting_correspondence['name_of_to_tel'] = accepting_correspondence['name_of_to_tel']
    requesting_correspondence['pobox_id'] = accepting_correspondence['pobox_id']

    print(f'\nUpdated correspondence...')
    print(f'accepting:\n{accepting_correspondence}')
    print(f'requesting:\n{requesting_correspondence}\n')

    saveget.save_correspondence(requesting_correspondence)
    saveget.save_correspondence(accepting_correspondence)
    #  -> Send message to both from_tels about the connection, the naming, and how to change.
    return f'Successfully connected {requesting_from_tel} to {from_tel}'
 

def update_the_requesting_morsel(requesting_from_tel, requester_to_tel, new_recipient):
    requester = saveget.get_sender(requesting_from_tel)
    requester['morsel'][requester_to_tel]['name_of_to_tel'] = new_recipient
    saveget.update_sender_and_morsel(requester)     


def add_requester_to_accepting_pobox(requesting_from_tel, accepting_correspondence):
    """Add viewer_data format to the accepting pobox. """
    accepting_pobox = saveget.get_pobox(accepting_correspondence['pobox_id'])
    viewer_data = accepting_pobox['viewer_data']
    viewer_data[requesting_from_tel] = dict(
        card_id = None  # This and other parameters assigned when the first card is sent using the re-assigned correspondence
    )
    saveget.save_pobox(accepting_pobox)

    
def delete_requester_from_former_pobox(requesting_from_tel, requesters_former_pobox_id):
    """Delete viewer_data from requesting pobox if (there is one!), and then delete the pobox if viewer_data is empty"""
    if not requesters_former_pobox_id:
        print(f'\n\n====>Debug in line 66 postoffice.connects, have no pobox_id for from_tel {requesting_from_tel}\n\n')
        return
    else:
        requesters_former_pobox = saveget.get_pobox(requesters_former_pobox_id)
        try:
            viewer_data = requesters_former_pobox['viewer_data']
            assert(len(viewer_data)==1)
            assert(requesters_former_pobox['key_operator']==requesting_from_tel)
        except AssertionError:
            raise
        viewer_data.pop(requesting_from_tel)
        saveget.save_pobox(requesters_former_pobox)


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
    


    