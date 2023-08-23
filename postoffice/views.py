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
        sender = saveget.get_sender(from_tel)
    except (TypeError, AssertionError):   
        return None
    else:
        return sender['conn'][to_tel]['pobox_id'] or new_pobox_id(sender, to_tel)


def new_pobox_id(sender, to_tel):
    """??? With new uuid, initialize the pobox and an empty viewer_data, update the viewer_data from the new pobox"""
    from_tel = sender['from_tel']
    pobox_id = str(uuid.uuid4())
    correspondence = saveget.get_correspondence(from_tel, to_tel)
    correspondence['pobox_id'] = pobox_id
    # make pobox and an empty viewer data, which will contain nothing until a call from postbox  
    pobox = dict(
        version=1, 
        pobox_id=pobox_id, 
        key_operator=from_tel, 
        heard_from=None,
        played_a_card = None,
        box_flag = True,
        viewer_data = dict(
            from_tel= dict()
            )
        )
    sender['morsel'][to_tel]['have_viewer'] = 'HaveViewer'
    # Save sender, morsel, pobox, correspondence, and an empty viewer_data
    saveget.update_sender_and_morsel(sender)    # pobox_id is set
    saveget.save_pobox(pobox)         # pobox is made and immediately used to update the new viewer_data
    saveget.save_correspondence(from_tel, to_tel, correspondence)
    return pobox_id


