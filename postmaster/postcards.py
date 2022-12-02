"""Read SQS to get new postcards, update AWS and update the data structure for the recipient web page"""

import time
import uuid

from filer import views as filerviews
from filer import lines
from filer import exceptions as filerexceptions


def new_postcard(from_tel, to_tel, **msg):
    wip = msg['wip']
    sent_at = msg['sent_at']
    match msg['context']:          # The detailed ordering requires the apparent duplication below
        case 'NewSenderFirst':
            profile_url = msg['profile_url']
            sender = create_new_sender(from_tel, profile_url)
            create_new_connection(sender, to_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            save_postcard(card)
            save_sender_and_morsel(sender)          # Save the new 'morsel' before deleting twilio's record
            delete_twilio_new_sender(sender)        # Delete the old twilio entry after the 'morsel' is available

        case 'NewRecipientFirst':
            sender = get_sender(from_tel)
            create_new_connection(sender, to_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            save_postcard(card)

        case 'NoViewer':
            sender = get_sender(from_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            save_postcard(card)

        case 'HaveViewer':
            sender = get_sender(from_tel)
            card = create_postcard_update_sender(sender, from_tel, to_tel, wip, sent_at)
            save_postcard(card)
            pobox = get_and_update_postbox(sender, to_tel)
            save_pobox(pobox)

    save_sender_and_morsel(sender)          # Is a re-save in case context == NewSenderFirst

    #
    #    ----------> someone should call update_viewer_data
    #






def save_sender_and_morsel(sender):
    save_sender(sender)
    morsel = make_morsel(sender)
    save_morsel(sender, morsel)

def create_new_sender(from_tel, profile_url):
    return dict(
        version = 1,
        from_tel = from_tel,
        profile_url = profile_url,
        name = 'from_tel derived',                       # Change by <from: name> command
        heard_from = time.time(),
        conn = {}
    )

def create_new_connection(sender, to_tel):
    from_tel = sender['from_tel']
    conn = sender['conn']
    conn[to_tel] = {}
    conn[to_tel]['to'] =  'kith or kin'                 # Used by twilio to customize sms to sender
    conn[to_tel]['from'] = 'from_tel derived'              
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
    pobox = get_pobox(pobox_id)    # pobox is created when a viewer is first made. pobox_id is found in sender.
    pobox['cardlists'][from_tel].append(card_id)
    return pobox

def make_morsel(sender):     
    """This a read-only, limited-info entry for twilio processing."""
    morsel =  {}
    for to_tel in sender['conn']: 
        morsel[to_tel] = {}
        morsel[to_tel]['from'] = sender['conn'][to_tel]['from']
        morsel[to_tel]['to'] = sender['conn'][to_tel]['to']
        morsel[to_tel]['have_viewer'] = bool(sender['conn'][to_tel]['pobox_id'])
    return morsel



    
def get_sender(from_tel):
    return filerviews._load_a_thing_using_key(key=f'sender/{from_tel}')

def save_sender(sender):
    filerviews._save_a_thing_using_key(thing=sender, key=f'sender/{sender["from_tel"]}')


def get_pobox(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'pobox_{pobox_id}')
def save_pobox(pobox):
    pobox_id = pobox['meta']['pobox_id']
    filerviews._save_a_thing_using_key(thing=pobox, key=f'pobox_{pobox_id}')


def save_postcard(postcard):
    card_id = postcard['card_id']
    filerviews._save_a_thing_using_key(thing=postcard, key=f'card_{card_id}')


def get_passkey_dictionary(from_tel):
    try:
        return filerviews._load_a_thing_using_key(f'passkey_{from_tel}')
    except filerexceptions.S3KeyNotFound:
        return None

def save_passkey_dictionary(passkey):
    from_tel =  passkey['from_tel']
    filerviews._save_a_thing_using_key(thing=passkey, key=f'passkey_{from_tel}')  


def save_morsel(sender, morsel):
    filerviews._save_a_thing_using_key(thing=morsel, key=f'free_tier/{sender["from_tel"]}')

def delete_twilio_new_sender(sender):
    filerviews._delete_a_thing_using_key(key=f'new_sender/{sender["from_tel"]}')

