""" Build the (static) website for a specified po_box from postbox.   """
import os
import json

from django.http.response import HttpResponse

from postoffice import test_cmds
from saveget import saveget


def update_viewer_data(pobox, viewer_data):              
    for from_tel in pobox['cardlists']:
        cardlist = pobox['cardlists'][from_tel]
        if not cardlist:        # No new cards to show, so on to the next sender's list
            continue    
        # There is a new card in pobox if viewer needs one
        viewer_card = viewer_data.get(from_tel, {})     
        if not viewer_card or viewer_card['play_count'] > 0:  # If initializing, or current has been played
            new_card_id, cardlist = cardlist[0], cardlist[1:]

            old_card_id = viewer_data.get('card_id', None)
            # Archive the old_card_id into some new data structure for each (receiver?).  Watch for None value
            
            new_card = saveget.get_postcard(new_card_id)
            viewer_card['card_id'] = new_card_id
            viewer_card['play_count'] = 0
            viewer_card['profile_url'] = new_card['profile_url']
            viewer_card['image_url'] = new_card['image_url']
            viewer_card['audio_url'] = new_card['audio_url']
            viewer_data[from_tel] = viewer_card
        

def return_playable_viewer_data(request, pobox_id):
    if pobox_id == 'test_pobox':    
        return _make_playable_viewer_data_for_testing(request, pobox_id)
    """Production"""
    return HttpResponse(content = json.dumps(viewer_data))


def played_this_card(request, pobox_id, card_id):
    pobox = saveget.get_pobox(pobox_id)
    viewer_data = saveget.get_viewer_data(pobox_id)
    card = saveget.get_postcard[card_id]
    from_tel = card['from_tel']
    card['play_count'] += 1
    viewer_data[from_tel]['play_count'] += 1
    update_viewer_data(pobox, viewer_data)
    return HttpResponse()

def validate_passkey(response, from_tel, passkey):
    if 'test' in from_tel.lower() or 'test' in passkey.lower():
        return HttpResponse(content=json.dumps('test_pobox'))
    else:
        return HttpResponse(content=json.dumps(None))

def _make_playable_viewer_data_for_testing(request, pobox_id):
    if not os.environ['TEST']:
        raise EnvironmentError
    saveget.clear_sqs_and_s3_for_testing
    viewer_data = test_cmds.make_two_sender_viewer_data()
    for from_tel in viewer_data:
        viewer_data[from_tel]['profile_url'] = img2    
        viewer_data[from_tel]['image_url'] = img1      
        viewer_data[from_tel]['audio_url'] = audio1     
    return HttpResponse(content = json.dumps(viewer_data))



















img1 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MM948cc579dc1dddcad6ff4545f7f68473/Media/ME18c2f52a4a3be36b2fb3609598187a13"
audio1 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE71fa37807272ce5bb2e13a7716dccbaf.mp3"
img2 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MMa8fc1b190596c0adf840f5d042ff442c/Media/ME0c9e8b0191dc098d8c60aca5a86b3a4c"
audio2 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE4b40cfb563d4890c1776b24f2a96099b.mp3"
img3 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MM1bbb4ad2a748f5c91145730bb1814bb6/Media/ME2a2ad0d70f188d079fb7bfebd28e0af0"
audio3 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE57fb3bc1c0b5776098ac78d450b1dd40.mp3"
