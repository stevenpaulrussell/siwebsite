import requests
import json
import os

from django.shortcuts import render
from django.http.response import HttpResponseRedirect


from .forms import ConnectionsForm

data_source = os.environ['POSTBOX_DATA_SOURCE']


def show_postcards_view(request, pobox_id):
    view_data = requests.get(f'{data_source}/viewer_data/{pobox_id}').json()  
    version = view_data['meta']['version']
    view_data.pop('meta')
    for from_tel, one_card_spec in view_data.items():
        one_card_spec['audio_id'] = f'{from_tel} audio'
        one_card_spec['played_this_card'] = f'/played/{one_card_spec["card_id"]}'
    return render(request, 'read.html', {'data_items': view_data, 'version': version})


def get_a_pobox_id(request):
    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        if form.is_valid():
            from_tel = form.cleaned_data['from_tel']
            passkey = form.cleaned_data['passkey']
            pobox_id_response = requests.get(f'{data_source}/validate_passkey/{from_tel}/{passkey}')
            pobox_id = pobox_id_response.json()
            if pobox_id:
                return HttpResponseRedirect(f'postbox/{pobox_id}')
            else:
                return render(request, 'to_connect.html', {'form': form})
    else:
        form = ConnectionsForm()
        return render(request, 'to_connect.html', {'form': form})


def instructions_view(request):
    return render(request, 'home.html')
