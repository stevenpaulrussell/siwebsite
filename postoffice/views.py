import requests
import json
import os
import time
import uuid


from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


from saveget import saveget
from .forms import ConnectionsForm
from .connects import get_passkey


@csrf_exempt
def get_a_pobox_id(request):
    """Use a form to enter from_tel and passkey. If the combo is not valid, 
    return the user to the form, where there should be some guide for this failure...
    With a valid combo, redirect the browser to the right pobox"""
    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        if form.is_valid():
            from_tel = form.cleaned_data['from_tel']
            passkey = form.cleaned_data['passkey']
            if 'test' in from_tel.lower() or 'test' in passkey.lower():
                return HttpResponseRedirect(f'player/postbox/test_pobox')
            else: 
                pobox_id = pobox_id_if_good_passkey(from_tel, passkey)
            if pobox_id:
                return HttpResponseRedirect(f'player/postbox/{pobox_id}')
    # else to any of the above, maybe want to respond more specifically, anyway:
    form = ConnectionsForm()
    return render(request, 'to_connect.html', {'form': form})


def pobox_id_if_good_passkey(from_tel, passkey):
    try:
        found_key, to_tel = get_passkey(from_tel)     #  TypeError is raised if get_passkey returns None
        assert(passkey==found_key)
    except (TypeError, AssertionError):   
        return None
    else:
        correspondence = saveget.get_correspondence(from_tel, to_tel)
        pobox_id = correspondence['pobox_id']   # user maybe recovering a pobox_id that already exists
        if not pobox_id:                        # But if there is no pobox_id so no pobox, 
            pobox_id = new_pobox_id(from_tel, to_tel, correspondence)   # make one, then update sender & correspondence, & save the pobox
        return pobox_id


def new_pobox_id(from_tel, to_tel, correspondence): # -> nake correspondence like an object, able to id iteself for storage
    """With new uuid, initialize the pobox and an empty viewer_data, then update viewer_data from the correspondence"""
    pobox_id = str(uuid.uuid4())
    correspondence['pobox_id'] = pobox_id
    # make pobox and an empty viewer data, which will contain nothing until a call from postbox  
    pobox = dict(
        version=1, 
        pobox_id=pobox_id, 
        key_operator=from_tel, 
        heard_from=None,
        played_a_card = None,
        box_flag = True,
        viewer_data = dict()   
        )
    sender = saveget.get_sender(from_tel)
    sender['morsel'][to_tel]['have_viewer'] = 'HaveViewer'
    saveget.update_sender_and_morsel(sender)    # pobox_id is set
    populate_new_pobox_view_data(from_tel, to_tel, pobox, correspondence)  # Setup viewer_data entry 
    saveget.save_pobox(pobox)         # pobox is made and immediately used to update the new viewer_data
    saveget.save_correspondence(correspondence)
    return pobox_id


def populate_new_pobox_view_data(from_tel, to_tel, pobox, correspondence):
    # populate with card tsken from correspondence['cardlist_unplayed']
    """General update for a single correspondence, responding to a single event: new_postbox, connect, new_card, card_played."""
    cardlist_unplayed = correspondence['cardlist_unplayed']
    card_id = correspondence['card_current'] = cardlist_unplayed.pop()
    postcard = saveget.get_postcard(card_id)
    pobox['viewer_data'][from_tel] = dict(
        card_id = card_id,
        play_count = 0,
        profile_url = postcard['profile_url'],
        image_url = postcard['image_url'],
        audio_url = postcard['audio_url'],
        to_tel = to_tel
    )


