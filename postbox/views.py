""" Build the (static) website for a specified po_box from postbox.   """
import os
import time
import json

from django.http.response import HttpResponse

from saveget import saveget
from . import tests


def update_viewer_data(pobox, viewer_data):       
    for from_tel in pobox['cardlists']:
        cardlist = pobox['cardlists'][from_tel]
        if not cardlist:     
            continue    # No new cards in pobox
        playable = viewer_data.get(from_tel, {}) 
        if playable:    
            if playable['play_count'] == 0:
                continue
            else:   # Card has been played, and there is a replacement
                retiring_card_id = playable['card_id']  # KeyError if there is no card yet!
                retiring_card = saveget.get_postcard(retiring_card_id)
                retiring_card['pobox_id'] =  pobox['meta']['pobox_id']
                retiring_card['retired_at'] = time.time()
                saveget.save_postcard(retiring_card)
        # Fill in with a new playable, either first one, or one has been retired 
        new_card_id, pobox['cardlists'][from_tel] = cardlist[0], cardlist[1:]  # swap a card from pobox to viewer_data
        new_card = saveget.get_postcard(new_card_id)
        playable['card_id'] = new_card_id
        playable['play_count'] = 0
        playable['profile_url'] = new_card['profile_url']
        playable['image_url'] = new_card['image_url']
        playable['audio_url'] = new_card['audio_url']
        viewer_data[from_tel] = playable
    saveget.save_pobox(pobox)
    saveget.save_viewer_data(viewer_data)
        

def return_playable_viewer_data(request, pobox_id):
    if 'test' in pobox_id:    
        viewer_data = _make_playable_viewer_data_for_testing()
    else:
        pobox = saveget.get_pobox(pobox_id)
        pobox['meta']['heard_from'] = time.time()
        viewer_data = saveget.get_viewer_data(pobox_id)
        update_viewer_data(pobox, viewer_data)
    return HttpResponse(content = json.dumps(viewer_data))


def played_this_card(request, pobox_id, card_id):
    if 'test' in pobox_id:
        return HttpResponse(content=json.dumps(f'Testing, got: pobox_id: {pobox_id};  card_id: {card_id}'))
    card = saveget.get_postcard(card_id)
    card['play_count'] += 1
    from_tel = card['from_tel']
    viewer_data = saveget.get_viewer_data(pobox_id)
    viewer_data[from_tel]['play_count'] += 1
    pobox = saveget.get_pobox(pobox_id)
    pobox['meta']['played_a_card'] = time.time()
    saveget.save_postcard(card)  # Save now to not overwrite a coming save in update_viewer_data
    update_viewer_data(pobox, viewer_data)
    return HttpResponse()

      
def _make_playable_viewer_data_for_testing():
    if not os.environ['TEST']:
        raise EnvironmentError
    saveget.clear_sqs_and_s3_for_testing
    viewer_data = tests.make_two_sender_viewer_data()
    for from_tel in viewer_data:
        viewer_data[from_tel]['profile_url'] = img2    
        viewer_data[from_tel]['image_url'] = img1      
        viewer_data[from_tel]['audio_url'] = audio1     
    return viewer_data



















img1 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MM948cc579dc1dddcad6ff4545f7f68473/Media/ME18c2f52a4a3be36b2fb3609598187a13"
audio1 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE71fa37807272ce5bb2e13a7716dccbaf.mp3"
img2 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MMa8fc1b190596c0adf840f5d042ff442c/Media/ME0c9e8b0191dc098d8c60aca5a86b3a4c"
audio2 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE4b40cfb563d4890c1776b24f2a96099b.mp3"
img3 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MM1bbb4ad2a748f5c91145730bb1814bb6/Media/ME2a2ad0d70f188d079fb7bfebd28e0af0"
audio3 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE57fb3bc1c0b5776098ac78d450b1dd40.mp3"
