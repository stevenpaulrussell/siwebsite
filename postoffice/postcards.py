"""Read SQS to get new postcards, update AWS and update the data structure for the recipient web page"""

import time
import uuid

from filer import views as filerviews
from filer import lines
from saveget import saveget


def new_postcard(from_tel, to_tel, event):
    wip = event['wip']
    sent_at = event['sent_at']
    match event['context']:          # The detailed ordering requires the apparent duplication below
        case 'NewSenderFirst':
            profile_url = event['profile_url']
            sender = create_new_sender(from_tel, profile_url)
            create_new_connection(sender, to_tel)
            card_id = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            
        case 'NewRecipientFirst':
            sender = saveget.get_sender(from_tel)
            create_new_connection(sender, to_tel)
            card_id = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)

        case 'NoViewer':
            sender = saveget.get_sender(from_tel)
            card_id = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)

        case 'HaveViewer':
            """Postcard put into pobox but update_viewer_data not called:  Viewer learns of card on its regular update."""
            sender = saveget.get_sender(from_tel)
            card_id = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            pobox_id = sender['conn'][to_tel]['pobox_id']
            update_pobox_new_card(from_tel, to_tel, pobox_id, card_id)

    saveget.update_sender_and_morsel(sender)    
    if event['context'] == 'NewSenderFirst':
        saveget.delete_twilio_new_sender(sender)        # Delete the old twilio entry after the 'morsel' is available


def create_new_sender(from_tel, profile_url):
    sender = dict(
        version = 1,
        from_tel = from_tel,
        profile_url = profile_url,
        heard_from = time.time(),
        conn = {}
    )
    sender['from'] =  create_default_using_from_tel(from_tel)        # Change by <from: name> command
    return sender

def create_default_using_from_tel(from_tel):
    return f'{from_tel[-4]} {from_tel[-3]} {from_tel[-2]} {from_tel[-1]}' 

def create_new_connection(sender, to_tel):
    from_tel = sender['from_tel']
    conn = sender['conn']
    conn[to_tel] = {}
    conn[to_tel]['to'] =  'kith or kin'                 # Used by twilio to customize sms to sender
    conn[to_tel]['from'] = sender['from']               # Change by <from: name> command, allows varying from depending on recipient
    conn[to_tel]['pobox_id'] = None                     # None until viewer is connected for (from_tel, to_tel). 
    msg = 'Sender {from_tel} using new to_tel {to_tel}.'
    new_conn_msg = lines.line(msg, from_tel=from_tel, to_tel=to_tel)
    filerviews.nq_admin_message(new_conn_msg)

def create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at):
    card_id = str(uuid.uuid4())
    card = dict(
        version = 1,
        card_id = card_id, 
        play_count = 0,                                  
        from_tel = from_tel,
        to_tel = to_tel,
        sent_at = sent_at,    
        recent_play = None,
        image_url = wip['image_url'],
        audio_url = wip['audio_url'],
        profile_url = sender['profile_url']       #  Viewer may see something different, but saving current profile with each card
    )
    sender['heard_from'] = sent_at
    this_conn = sender['conn'][to_tel]
    this_conn['recent_card_id'] = card_id
    this_conn['recent_card_when'] = sent_at
    saveget.save_postcard(card)
    return card_id

def update_pobox_new_card(from_tel, to_tel, pobox_id, card_id):
    pobox = saveget.get_pobox(pobox_id)        
    pobox['cardlists'][from_tel].append(card_id)
    saveget.save_pobox(pobox)



