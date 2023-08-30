import os
import json
import time


from saveget import saveget

from . import postcards, connects


def interpret_one_event(event):
    tel_id = event['tel_id']
    svc_id = event['svc_id']
    event_type = event['event_type']
    match event_type:
        case 'new_postcard':
            postcards.new_postcard(tel_id, svc_id, event)
            return 
        case 'profile':
            sender = saveget.get_sender(tel_id)
            sender['profile_url'] = event['profile_url']
            saveget.update_sender_and_morsel(sender)
            return f'OK, your profile image has been updated.'
        case 'passkey':
            passkey=event['passkey']
            to_store = dict(tel_id=tel_id, svc_id=svc_id, passkey=event['passkey'], expire=event['expire'])
            saveget.save_passkey_dictionary(to_store)
            return f'Your passkey <{passkey}> is now good. It will expire 24 hours from now.'
        case 'text_was_entered':
            message = handle_entered_text_event(tel_id, svc_id, event['text'])
            return message
        case 'played_it':
            handle_played_it_event(event)            
        case _:
            """ Send admin an error message or in test raise exception"""
            message = f'whoops, do not recognize command {event_type}.'

def handle_entered_text_event(tel_id, svc_id, text): 
    if 'connect' in text:
        result = connects.connect_joining_sender_to_lead_sender_pobox(tel_id, svc_id, text)
        return result

    if 'from:' in text:
        try:    
            cmd, name = [word.strip() for word in text.split(' ')]
            assert cmd == 'from:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        sender = saveget.get_sender(tel_id)
        if sender['sender_moniker'] == postcards.create_default_using_tel_id(tel_id):      # Had been using the default name, so change all
            sender['sender_moniker'] = name
            for each_svc_id in sender['morsel']:
                sender['morsel'][each_svc_id]['sender_moniker'] = name
        else:
            sender['morsel'][svc_id]['from'] = name
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
        sender = saveget.get_sender(tel_id)
        former_name = sender['morsel'][svc_id]['recipient_moniker']
        sender['morsel'][svc_id]['recipient_moniker'] = new_name
        saveget.update_sender_and_morsel(sender)
        return f'Renamed recipient {former_name} to {new_name}'

    else:
        return f"Do not recognize commmand '{text}'. Send '?' for more help."


def handle_played_it_event(event):
    pobox_id = event['pobox_id']
    card_id = event['card_id']
    pobox = saveget.get_pobox(pobox_id)
    card = saveget.get_postcard(card_id)
    card['play_count'] += 1
    card['pobox_id'] = pobox_id
    tel_id, svc_id = card['boxlink']
    boxlink = saveget.get_boxlink(tel_id, svc_id)
    if boxlink['cardlist_unplayed'] != []:
        postcards.push_cards_along(boxlink, pobox)
    saveget.save_boxlink(boxlink)
    saveget.save_pobox(pobox)



