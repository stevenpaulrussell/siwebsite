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
        case 'played_it':
            
        case _:
            """ Send admin an error message or in test raise exception"""
            message = f'whoops, do not recognize command {event_type}.'

def handle_entered_text_event(from_tel, to_tel, text): 
    if 'connect' in text:
        result = connects.connect_joining_sender_to_lead_sender_pobox(from_tel, to_tel, text)
        return result

    if 'from:' in text:
        try:    
            cmd, name = [word.strip() for word in text.split(' ')]
            assert cmd == 'from:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        sender = saveget.get_sender(from_tel)
        if sender['name_of_from_tel'] == postcards.create_default_using_from_tel(from_tel):      # Had been using the default name, so change all
            sender['name_of_from_tel'] = name
            for each_to_tel in sender['morsel']:
                sender['morsel'][each_to_tel]['name_of_from_tel'] = name
        else:
            sender['morsel'][to_tel]['from'] = name
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
        former_name = sender['morsel'][to_tel]['name_of_to_tel']
        sender['morsel'][to_tel]['name_of_to_tel'] = new_name
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
    from_tel, to_tel = card['correspondence']
    correspondence = saveget.get_correspondence(from_tel, to_tel)
    if correspondence['cardlist_unplayed'] != []:
        postcards.push_cards_along(correspondence, pobox)
    saveget.save_correspondence(correspondence)
    saveget.save_pobox(pobox)



