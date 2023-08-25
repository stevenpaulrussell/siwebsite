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
            correspondence = create_new_correspondence_update_morsel(sender, to_tel)
            card_id = create_postcard(sender, from_tel, to_tel, wip, sent_at)
            correspondence['cardlist_unplayed'].append(card_id)
            
        case 'NewRecipientFirst':
            sender = saveget.get_sender(from_tel)
            correspondence = create_new_correspondence_update_morsel(sender, to_tel)
            card_id = create_postcard(sender, from_tel, to_tel, wip, sent_at)
            correspondence['cardlist_unplayed'].append(card_id)

        case 'NoViewer':
            sender = saveget.get_sender(from_tel)
            card_id = create_postcard(sender, from_tel, to_tel, wip, sent_at)
            correspondence = saveget.get_correspondence(from_tel, to_tel)
            correspondence['cardlist_unplayed'].append(card_id)

        case 'HaveViewer':
            """Postcard put into pobox but update_viewer_data not called:  Viewer learns of card on its regular update."""
            sender = saveget.get_sender(from_tel)
            card_id = create_postcard(sender, from_tel, to_tel, wip, sent_at)
            correspondence = saveget.get_correspondence(from_tel, to_tel)
            correspondence['cardlist_unplayed'].append(card_id)
            update_pobox_new_card(correspondence)

    saveget.update_sender_and_morsel(sender)    
    saveget.save_correspondence(correspondence)
    if event['context'] == 'NewSenderFirst':
        saveget.delete_twilio_new_sender(sender)        # Delete the old twilio entry after the 'morsel' is available


def create_new_sender(from_tel, profile_url):
    name_of_from_tel =  create_default_using_from_tel(from_tel)
    sender = dict(
        version = 1,
        from_tel = from_tel,
        profile_url = profile_url,
        name_of_from_tel = name_of_from_tel,  
        morsel = {}             # morsel made by each create_new_correspondence 
    )
    return sender

def create_default_using_from_tel(from_tel):  # Set as a call so later can test if the user is changing from the default
    return f'{from_tel[-4]} {from_tel[-3]} {from_tel[-2]} {from_tel[-1]}'


def create_new_correspondence_update_morsel(sender, to_tel):
    from_tel = sender['from_tel']
    correspondence = dict(
        from_tel = from_tel,
        to_tel = to_tel,
        version = 1,
        name_of_from_tel = sender['name_of_from_tel'],
        name_of_to_tel = 'kith or kin',
        pobox_id = from_tel,  # pobox_id is assigned by 'connect' commands
        most_recent_arrival_timestamp = time.time(),
        cardlist_played = [],
        card_current = None,
        cardlist_unplayed = []
    )
    morsel = sender['morsel']
    morsel[to_tel] = dict(
        name_of_from_tel=sender['name_of_from_tel'],
        name_of_to_tel = 'kith or kin',
        have_viewer = False
    )
    msg = 'Sender {from_tel} using new to_tel {to_tel}.'
    new_corr_msg = lines.line(msg, from_tel=from_tel, to_tel=to_tel)
    filerviews.nq_admin_message(new_corr_msg)
    return correspondence


def create_postcard(sender, from_tel, to_tel, wip, sent_at):
    """Make a postcard from received event data"""
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
    saveget.save_postcard(card)
    return card_id


def update_pobox_new_card(correspondence):
    """Called when a new card has arrived and a viewer exists. Update the viewer_data only if the current card has not played. """
    pobox = saveget.get_pobox(correspondence['pobox_id'])
    from_tel = correspondence['from_tel'] 
    viewer_data_item = pobox['viewer_data'][from_tel]    # from_tel key was set when pobox_id was assigned...
    if viewer_data_item['play_count'] > 0:
        push_cards_along(correspondence, pobox)
    # correspondence is changed, but is saved by the caller
    saveget.save_pobox(pobox)


def push_cards_along(correspondence, pobox):
    """Called to push cards if events played_this_card or new_card show the current card should be moved. """
    correspondence['card_current'] = card_id =  correspondence['cardlist_unplayed'].pop()  
    correspondence['cardlist_played'].append(card_id)                
    from_tel, to_tel = correspondence['from_tel'], correspondence['to_tel']
    postcard = saveget.get_postcard(card_id)   
    pobox['viewer_data'][from_tel] = dict(
        card_id = card_id,
        play_count = 0,
        profile_url = postcard['profile_url'],
        image_url = postcard['image_url'],
        audio_url = postcard['audio_url'],
        to_tel = to_tel
    )    





