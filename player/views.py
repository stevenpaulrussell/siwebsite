import requests
import json
import os

from django.shortcuts import render
from django.http.response import HttpResponseRedirect




data_source = os.environ['POSTBOX_DATA_SOURCE']


def show_postcards_view(request, pobox_id):
    view_data = requests.get(f'{data_source}/player/viewer_data/{pobox_id}').json()  
    version = view_data['meta']['version']
    view_data.pop('meta')
    for from_tel, one_card_spec in view_data.items():
        one_card_spec['audio_id'] = f'{from_tel} audio'
        one_card_spec['played_this_card'] = f'/played/{pobox_id}/{one_card_spec["card_id"]}'
    return render(request, 'read.html', {'data_items': view_data, 'version': version})


