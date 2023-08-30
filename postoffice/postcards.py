"""Read SQS to get new postcards, update AWS and update the data structure for the recipient web page"""

import time
import uuid

from filer import views as filerviews
from filer import lines
from saveget import saveget


def new_postcard(tel_id, svc_id, event):
    wip = event['wip']
    sent_at = event['sent_at']
    match event['context']:          # The detailed ordering requires the apparent duplication below
        case 'NewSenderFirst':
            profile_url = event['profile_url']
            sender = create_new_sender(tel_id, profile_url)
            boxlink = create_new_boxlink_update_morsel(sender, svc_id)
            card_id = create_postcard(sender, tel_id, svc_id, wip, sent_at)
            boxlink['cardlist_unplayed'].append(card_id)
            
        case 'NewRecipientFirst':
            sender = saveget.get_sender(tel_id)
            boxlink = create_new_boxlink_update_morsel(sender, svc_id)
            card_id = create_postcard(sender, tel_id, svc_id, wip, sent_at)
            boxlink['cardlist_unplayed'].append(card_id)

        case 'NoViewer':
            sender = saveget.get_sender(tel_id)
            card_id = create_postcard(sender, tel_id, svc_id, wip, sent_at)
            boxlink = saveget.get_boxlink(tel_id, svc_id)
            boxlink['cardlist_unplayed'].append(card_id)

        case 'HaveViewer':
            """Postcard put into pobox but update_viewer_data not called:  Viewer learns of card on its regular update."""
            sender = saveget.get_sender(tel_id)
            card_id = create_postcard(sender, tel_id, svc_id, wip, sent_at)
            boxlink = saveget.get_boxlink(tel_id, svc_id)
            boxlink['cardlist_unplayed'].append(card_id)
            update_pobox_new_card(boxlink)

    saveget.update_sender_and_morsel(sender)    
    saveget.save_boxlink(boxlink)
    if event['context'] == 'NewSenderFirst':
        saveget.delete_twilio_new_sender(sender)        # Delete the old twilio entry after the 'morsel' is available


def create_new_sender(tel_id, profile_url):
    sender_moniker =  create_default_using_tel_id(tel_id)
    sender = dict(
        version = 1,
        tel_id = tel_id,
        profile_url = profile_url,
        sender_moniker = sender_moniker,  
        morsel = {}             # morsel made by each create_new_boxlink 
    )
    return sender

def create_default_using_tel_id(tel_id):  # Set as a call so later can test if the user is changing from the default
    return f'{tel_id[-4]} {tel_id[-3]} {tel_id[-2]} {tel_id[-1]}'


def create_new_boxlink_update_morsel(sender, svc_id):
    tel_id = sender['tel_id']
    boxlink = dict(
        tel_id = tel_id,
        svc_id = svc_id,
        version = 1,
        sender_moniker = sender['sender_moniker'],
        recipient_moniker = 'kith or kin',
        pobox_id = None,     # pobox_id is assigned by 'connect' commands.  
        most_recent_arrival_timestamp = time.time(),
        cardlist_played = [],
        card_current = None,
        cardlist_unplayed = []
    )
    morsel = sender['morsel']
    morsel[svc_id] = dict(
        sender_moniker=sender['sender_moniker'],
        recipient_moniker = 'kith or kin',
        have_viewer = False
    )
    msg = 'Sender {tel_id} using new svc_id {svc_id}.'
    new_corr_msg = lines.line(msg, tel_id=tel_id, svc_id=svc_id)
    filerviews.nq_admin_message(new_corr_msg)
    return boxlink


def create_postcard(sender, tel_id, svc_id, wip, sent_at):
    """Make a postcard from received event data"""
    card_id = str(uuid.uuid4())
    card = dict(
        version = 1,
        card_id = card_id, 
        play_count = 0,                                  
        tel_id = tel_id,
        svc_id = svc_id,
        sent_at = sent_at,    
        recent_play = None,
        image_url = wip['image_url'],
        audio_url = wip['audio_url'],
        profile_url = sender['profile_url']       #  Viewer may see something different, but saving current profile with each card
    )
    saveget.save_postcard(card)
    return card_id


def update_pobox_new_card(boxlink):
    """Called when a new card has arrived and a viewer exists. Update the viewer_data only if the current card has not played. """
    pobox = saveget.get_pobox(boxlink['pobox_id'])
    tel_id = boxlink['tel_id'] 
    viewer_data_item = pobox['viewer_data'][tel_id]    # tel_id key was set when pobox_id was assigned...
    try:
        if viewer_data_item['play_count'] > 0:
            push_cards_along(boxlink, pobox)
    except KeyError:  # no viewer_data for this sender because this is the first card
        push_cards_along(boxlink, pobox, initializing=True)
    # boxlink is changed, but is saved by the caller
    saveget.save_pobox(pobox)


def push_cards_along(boxlink, pobox, initializing=False):
    """Called to push cards if events played_this_card or new_card show the current card should be moved. """
    tel_id, svc_id = boxlink['tel_id'], boxlink['svc_id']
    if initializing:
        pass   # No card to move from [card_current] into cardlist_played
    else:
        boxlink['cardlist_played'].append(boxlink['card_current']) 
    card_id = boxlink['card_current'] =  boxlink['cardlist_unplayed'].pop()               
    postcard = saveget.get_postcard(card_id)   
    pobox['viewer_data'][tel_id] = dict(
        card_id = card_id,
        play_count = 0,
        profile_url = postcard['profile_url'],
        image_url = postcard['image_url'],
        audio_url = postcard['audio_url'],
        svc_id = svc_id
    )    





