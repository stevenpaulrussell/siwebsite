"""Instructions and marketing web views.
    Redirect to 'connect' a viewer to a specific po_box using the app postoffice. 
    Tickles receiver to dq cmds and return admin messages"""


import requests
import json
import os

from django.shortcuts import render
from django.http.response import HttpResponseRedirect


from .forms import ConnectionsForm

data_source = os.environ['POSTBOX_DATA_SOURCE']

def get_a_pobox_id(request):
    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        if form.is_valid():
            from_tel = form.cleaned_data['from_tel']
            passkey = form.cleaned_data['passkey']
            if 'test' in from_tel.lower() or 'test' in passkey.lower():
                return HttpResponseRedirect(f'player/postbox/test_pobox')
            else: 
                pobox_id_url = f'{data_source}/validate_me/{from_tel}/{passkey}'
                pobox_id = requests.get(pobox_id_url).json()
            if pobox_id:
                return HttpResponseRedirect(f'player/postbox/{pobox_id}')
    # else to any of the above, maybe want to respond more specifically, anyway:
    form = ConnectionsForm()
    return render(request, 'to_connect.html', {'form': form})


def instructions_view(request):
    return render(request, 'home.html')
