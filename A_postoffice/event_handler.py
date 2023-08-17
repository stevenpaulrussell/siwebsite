import os
import json
import time


from saveget import saveget

from . import postcards, connects


def interpret_one_event(event):
    from_tel = event['from_tel']
    to_tel = event['to_tel']
    event_type = event['event_type']
    match event_type:
        case 'new_postcard':
            postcards.new_postcard(from_tel, to_tel, event)
            return 
        case 'profile':
            sender = saveget.get_sender(from_tel)
            sender['profile_url'] = event['profile_url']
            saveget.update_sender_and_morsel(sender)
            return f'OK, your profile image has been updated.'
        case 'passkey':
            passkey=event['passkey']
            to_store = dict(from_tel=from_tel, to_tel=to_tel, passkey=event['passkey'], expire=event['expire'])
            saveget.save_passkey_dictionary(to_store)
            return f'Your passkey <{passkey}> is now good. It will expire 24 hours from now.'
        case 'text_was_entered':
            message = handle_entered_text_event(from_tel, to_tel, event['text'])
            return message
        case _:
            """ Send admin an error message or in test raise exception"""
            message = f'whoops, do not recognize command {event_type}.'

def handle_entered_text_event(from_tel, to_tel, text): 
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



