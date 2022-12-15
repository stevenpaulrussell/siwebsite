from django.shortcuts import render

from django.http.response import HttpResponseRedirect

import requests
import json
import os

from .forms import ConnectionsForm


data_source = os.environ['POSTBOX_DATA_SOURCE']

def get_po_box_uuid(from_tel, connector):
    po_box_uuid_response = requests.get(f'{data_source}/connect/{from_tel}/{connector}')
    try:
        return po_box_uuid_response.json()
    except json.JSONDecodeError:
        return None


def get_po_box_data(po_box_uuid):
    reading_desk_response = requests.get(f'{data_source}/read/{po_box_uuid}')
    try:
        return reading_desk_response.json()
    except json.JSONDecodeError:
        return None


def instructions_view(request):
    return render(request, 'home.html')


def make_connection_view(request):
    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        if form.is_valid():
            from_tel = form.cleaned_data['from_tel']
            connector = form.cleaned_data['connector']
            po_box_uuid = get_po_box_uuid(from_tel, connector)
            return HttpResponseRedirect(f'postbox/{po_box_uuid}')
    else:
        form = ConnectionsForm()
        return render(request, 'to_connect.html', {'form': form})


def show_postcards_view(request, po_box_uuid, test_id=None):
    po_box_data = get_po_box_data(po_box_uuid)
    my_desk = po_box_data['my_desk']
    version =  po_box_data['version']
    data_items = {}
    for from_tel, one_card_spec in my_desk.items():
        card_uuid = one_card_spec['card_uuid']
        one_card_spec['postcard_audio_id'] = f'{from_tel} audio'
        one_card_spec['played_this_card'] = f'{data_source}/played/{card_uuid}'
        data_items[from_tel] = one_card_spec
    if test_id=='A':
        return render(request, 'testA.html', {'data_items': data_items, 'version': version})
    if test_id=='B':
        return render(request, 'testB.html', {'data_items': data_items, 'version': version})
    if test_id=='C':
        return render(request, 'testC.html', {'data_items': data_items, 'version': version})
    if test_id=='D':
        return render(request, 'testD.html', {'data_items': data_items, 'version': version})
    # else !
    return render(request, 'read.html', {'data_items': data_items, 'version': version})



def test_a_postcard_view(request, test_id):
    return show_postcards_view(request, po_box_uuid='27f12208-2dfd-4f85-b292-f0dc710a54a4-pobox', test_id=test_id)


