"""Read SQS to get new postcards, update AWS and update the data structure for the recipient web page"""

import time
import uuid

from filer import views as filerviews
from filer import lines

from postoffice.views import update_viewer_data

from . import saveget


def new_postcard(from_tel, to_tel, msg):
    wip = msg['wip']
    sent_at = msg['sent_at']
    match msg['context']:          # The detailed ordering requires the apparent duplication below
        case 'NewSenderFirst':
            profile_url = msg['profile_url']
            sender = create_new_sender(from_tel, profile_url)
            create_new_connection(sender, to_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            saveget.save_postcard(card)

        case 'NewRecipientFirst':
            sender = saveget.get_sender(from_tel)
            create_new_connection(sender, to_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            saveget.save_postcard(card)

        case 'NoViewer':
            sender = saveget.get_sender(from_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            saveget.save_postcard(card)

        case 'HaveViewer':
            """Postcard put into pobox but update_viewer_data not called:  Viewer learns of card on its regular update."""
            sender = saveget.get_sender(from_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            pobox = get_and_update_postbox(sender, to_tel)
            saveget.save_postcard(card)
            saveget.save_pobox(pobox)
            viewer_data = saveget.get_viewer_data(pobox['meta']['pobox_id'])
            update_viewer_data(pobox, viewer_data)
            saveget.save_viewer_data(viewer_data)


    saveget.update_sender_and_morsel(sender)    # pobox_id is set
    if msg['context'] == 'NewSenderFirst':
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
        plays = 0,                                  
        from_tel = from_tel,
        to_tel = to_tel,
        sent_at = sent_at,    
        image_url = wip['image_url'],
        audio_url = wip['audio_url'],
        profile_url = sender['profile_url']       #  Viewer may see something different, but saving current profile with each card
    )
    sender['heard_from'] = sent_at
    this_conn = sender['conn'][to_tel]
    this_conn['recent_card_id'] = card_id
    this_conn['recent_card_when'] = sent_at
    return card

def get_and_update_postbox(sender, to_tel):
    from_tel = sender['from_tel']
    pobox_id =  sender['conn'][to_tel]['pobox_id']
    card_id = sender['conn'][to_tel]['recent_card_id']
    pobox = saveget.get_pobox(pobox_id)    # pobox is created when a viewer is first made. pobox_id is found in sender.
    pobox['cardlists'][from_tel].append(card_id)
    return pobox
