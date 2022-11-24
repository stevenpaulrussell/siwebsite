"""Read SQS to get new postcards, update AWS and update the data structure for the recipient web page"""

import time
import uuid

from filer import views as filerviews
from filer import lines



def first_postcard(from_tel, to_tel, **msg):
    """Creates the sender with nothing in connections"""
    wip = msg['wip']
    profile_url = msg['profile_url']
    sender = dict(
        version = 1,
        from_tel = from_tel,
        profile_photo_url = profile_url,
        name = 'from_tel derived',                       # Change by <from: name> command
        heard_from = time.time(),
        conn = {}
    )
    save_sender(sender)
    new_postcard(from_tel, to_tel, **msg)
    delete_twilio_new_sender(sender)


def new_postcard(from_tel, to_tel, **msg):
    """ Writes the postcard,  updates sender, updates the pobox if there is one """
    wip = msg['wip']                
    sender = get_sender(from_tel)
    profile_photo_url = sender['profile_photo_url']
    card_id, sent_at = make_card_entry(from_tel, to_tel, wip, profile_photo_url)
    sender['heard_from'] = sent_at
    conn = sender['conn']
    if to_tel not in conn:              
        conn[to_tel] = {}
        conn[to_tel]['to'] =  'kith or kin',                    # Used by twilio to customize sms to sender
        conn[to_tel]['from'] = 'from_tel derived'              
        conn[to_tel]['pobox_id'] = None                     # None until viewer is connected for (from_tel, to_tel). 
        msg = 'Sender {from_tel} using new to_tel {to_tel}.'
        new_postcard_msg = lines.line(msg, from_tel=from_tel, to_tel=to_tel)
        filerviews.nq_admin_message(new_postcard_msg)
    conn[to_tel]['recent_card_id'] = card_id
    conn[to_tel]['recent_card_when'] = sent_at
    save_sender(sender)

    pobox_id =  conn[to_tel]['pobox_id']
    if pobox_id:
        pobox = get_pobox(pobox_id)    # pobox is created when a viewer is first made. pobox_id is found in sender.
        pobox[from_tel].append(card_id)
        save_pobox(pobox)

        
def make_card_entry(from_tel, to_tel, wip, profile_photo_url):
    card_id = str(uuid.uuid4())
    sent_at = time.time()  
    card = dict(
        version = 1,
        id = card_id, 
        plays = 0,                                  
        from_tel = from_tel,
        to_tel = to_tel,
        sent_at = sent_at,    
        image_url = wip['image_url'],
        audio_url = wip['audio_url'],
        profile_url = profile_photo_url       #  Viewer may see something different
    )
    save_card(card)
    return card_id, sent_at


def save_card(card):
    filerviews._save_a_thing_using_key(thing=card, key=f'card_{"id"}')

    
def get_sender(from_tel):
    return filerviews._load_a_thing_using_key(key=f'sender/{from_tel}')

def save_sender(sender):
    filerviews._save_a_thing_using_key(thing=sender, key=f'sender/{sender["from_tel"]}')
    save_twilio_free_tier(sender)     # Changes to sender may require changes to be read by twilio



def get_pobox(pobox_id):
    return filerviews._load_a_thing_using_key(key=f'pobox_{pobox_id}')

def save_pobox(pobox):
    filerviews._save_a_thing_using_key(thing=pobox, key=f'pobox_{pobox["id"]}')

    
def save_twilio_free_tier(sender):      #  Called by save_sender
    """This a read-only, limited-info entry for twilio processing."""
    morsel =  sender['conn'].copy()
    for this_connection in morsel.values():     # Want to leave 'from' and 'to' as only keys
        for key in this_connection:
            if key not in ('from', 'to'):
                this_connection.pop(key)
    filerviews._save_a_thing_using_key(thing=morsel, key=f'free_tier/{sender["from_tel"]}')


def delete_twilio_new_sender(sender):
    filerviews._delete_a_thing_using_key(key=f'new_sender/{sender["from_tel"]}')

