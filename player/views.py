import requests
import json
import os

from django.shortcuts import render
from django.http.response import HttpResponseRedirect

from postoffice import cmdline

from .forms import ConnectionsForm


#data_source = os.environ['POSTBOX_DATA_SOURCE']

def get_pobox_id(from_tel, connector):
    pobox_id_response = requests.get(f'{data_source}/connect/{from_tel}/{connector}')
    try:
        return pobox_id_response.json()
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
            pobox_id = get_pobox_id(from_tel, connector)
            return HttpResponseRedirect(f'postbox/{pobox_id}')
    else:
        form = ConnectionsForm()
        return render(request, 'to_connect.html', {'form': form})


def show_postcards_view(request, pobox_id):
    view_data = cmdline.make_playable_viewer_data()   # replaces the GET from a different web address
    view_data = requests.get('/viewer_data/some_postbox_id')   # replaces the GET from a different web address
    version = view_data['meta']['version']
    view_data.pop('meta')
    for from_tel, one_card_spec in view_data.items():
        one_card_spec['audio_id'] = f'{from_tel} audio'
        one_card_spec['played_this_card'] = f'/played/{one_card_spec["card_id"]}'
    return render(request, 'read.html', {'data_items': view_data, 'version': version})

