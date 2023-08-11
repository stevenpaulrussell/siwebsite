import os
import json
import time


from saveget import saveget
from filer import twilio_cmds

from . import postcards, connects

def dq_and_do_one_cmd():
    cmd_item = saveget.get_one_sqs_event()
    if cmd_item:    
        message = interpret_one_cmd(cmd_item)
        if message:
            from_tel = cmd_item['from_tel']
            to_tel = cmd_item['to_tel']
            twilio_cmds.sms_back(from_tel=from_tel, to_tel=to_tel, message_key=message)
    return cmd_item  # Returns None if sqs was empty, signaling no need to re-invoke
    

def interpret_one_cmd(cmd_dict):
    from_tel = cmd_dict['from_tel']
    to_tel = cmd_dict['to_tel']
    cmd = cmd_dict['event']
    match cmd:
        case 'new_postcard':
            postcards.new_postcard(from_tel, to_tel, cmd_dict)
            return 
        case 'profile':
            sender = saveget.get_sender(from_tel)
            sender['profile_url'] = cmd_dict['profile_url']
            saveget.update_sender_and_morsel(sender)
            return f'OK, your profile image has been updated.'
        case 'passkey':
            passkey=cmd_dict['passkey']
            to_store = dict(from_tel=from_tel, to_tel=to_tel, passkey=cmd_dict['passkey'], expire=cmd_dict['expire'])
            saveget.save_passkey_dictionary(to_store)
            return f'Your passkey <{passkey}> is now good. It will expire 24 hours from now.'
        case 'cmd_general':
            message = handle_possible_cmd_general(from_tel, to_tel, cmd_dict['text'])
            return message
        case _:
            """ Send admin an error message or in test raise exception"""
            message = f'whoops, do not recognize command {cmd}.'

def handle_possible_cmd_general(from_tel, to_tel, text): 
    if 'connect' in text:
        """ --> Call connects.disconnect_viewer and  connects.connect_requester_to_granted_pobox"""
        lead_sender = saveget.get_sender(from_tel)
        cmd, joiner_from_tel, passkey_literal, passkey = [word.strip() for word in text.split(' ')]
        try:    
            joiner = saveget.get_sender(joiner_from_tel)
            found_key, joiner_to_tel = connects.get_passkey(joiner_from_tel)     # Raises TypeError if no passkey
            assert(found_key == passkey)
            assert cmd == 'connect'
            assert passkey_literal == 'passkey'
            assert len(passkey) == 4
        except (ValueError, AssertionError, TypeError):
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        connects.disconnect_from_viewer(joiner, joiner_to_tel)
        message = connects.connect_joiner_to_lead_sender_pobox(joiner, lead_sender, joiner_to_tel, to_tel)
        saveget.update_sender_and_morsel(lead_sender)
        saveget.update_sender_and_morsel(joiner)
        return message

    if 'from:' in text:
        try:    
            cmd, name = [word.strip() for word in text.split(' ')]
            assert cmd == 'from:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        sender = saveget.get_sender(from_tel)
        if sender['from'] == postcards.create_default_using_from_tel(from_tel):      # Had been using the default name, so change all
            sender['from'] = name
            for some_to_tel in sender['conn']:
                sender['conn'][some_to_tel]['from'] = name
        else:
            sender['conn'][to_tel]['from'] = name
        saveget.update_sender_and_morsel(sender)
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
        saveget.update_sender_and_morsel(sender)
        return f'Renamed recipient {former_name} to {new_name}'

    else:
        return f"Do not recognize commmand '{text}'. Send '?' for more help."



