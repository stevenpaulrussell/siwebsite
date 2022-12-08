import os
import json
import time


from . import saveget, postcards, connects
from filer import exceptions


def interpret_one_cmd(cmd_json):
    cmd_dict = json.loads(cmd_json)
    from_tel = cmd_dict['from_tel']
    to_tel = cmd_dict['to_tel']
    cmd = cmd_dict['cmd']
    match cmd:
        case 'new_postcard':
            message = postcards.new_postcard(from_tel, to_tel, cmd_dict)
        case 'profile':
            sender = saveget.get_sender(from_tel)
            sender['profile_url'] = cmd_dict['profile_url']
            message = f'OK, your profile image has been updated.'
            saveget.save_sender(sender)
            return message
        case 'cmd_general':
            message = handle_possible_cmd_general(from_tel, to_tel, cmd_dict['text'])
            return message
        case _:
            """ Send admin an error message or in test raise exception"""

def handle_possible_cmd_general(from_tel, to_tel, text): 
    if text == 'connector':
        passkey = connects.set_passkey(from_tel, to_tel)
        msg = f'Your passkey is "{passkey}".  It is valid for one day.'
        return msg

    if 'connect' in text and text != 'connector':
        """ --> Call connects.disconnect_viewer and  connects.connect_requester_to_granted_pobox"""
        sender = saveget.get_sender(from_tel)
        cmd, request_from_tel, connector_literal, connector = [word.strip() for word in text.split(' ')]
        try:    
            assert cmd == 'connect'
            assert connector_literal == 'connector'
            assert len(connector) == 4
            request_sender = saveget.get_sender(request_from_tel)
            r_to_tel = connects.check_passkey(request_from_tel, connector)['to_tel']      # Throws KeyError if no match
        except (ValueError, AssertionError, KeyError):
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        if request_sender['conn'][r_to_tel]['pobox_id']:  # Requester has an existing pobox_id, so need to update pobox and viewer data.
            connects.disconnect_from_viewer(request_sender, r_to_tel)
        connects.connect_requester_to_granted_pobox(request_sender, sender, r_to_tel, to_tel)
        saveget.save_sender(sender)
        saveget.save_sender(request_sender)
        print(f'')
        return 'Successful connect message'

    if 'from:' in text:
        try:    
            cmd, name = [word.strip() for word in text.split(' ')]
            assert cmd == 'from:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        sender = saveget.get_sender(from_tel)
        sender['conn'][to_tel]['from'] = name
        saveget.save_sender(sender)
        return f'You will now be identified to others in your sending group by {name} rather than by your sending telephone number.'

    if 'to:' in text and len(text.split(' '))==2:
        try:    
            cmd, new_name = [word.strip() for word in text.split(' ')]
            assert cmd == 'to:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        sender = saveget.get_sender(from_tel)
        former_name = sender['conn'][to_tel]['to']
        sender['conn'][to_tel]['to'] = new_name
        saveget.save_sender(sender)
        return f'Renamed recipient {former_name} to {new_name}'

    else:
        return f"Do not recognize commmand '{text}'. Send '?' for more help."



