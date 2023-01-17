"""Instructions and marketing web views.
    Redirect to 'connect' a viewer to a specific po_box using the app postoffice. 
    Tickles receiver to dq cmds and return admin messages"""


import requests
import json
import os

from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect

from postoffice.cmds import dq_and_do_one_cmd
from saveget import saveget
from .forms import ConnectionsForm

data_source = os.environ['POSTBOX_DATA_SOURCE']

def get_a_pobox_id(request):
    if request.method == 'POST':
        form = ConnectionsForm(request.POST)
        if form.is_valid():
            from_tel = form.cleaned_data['from_tel']
            passkey = form.cleaned_data['passkey']

# ---------> if os.environ['TEST'] == 'TEST', then bypass the form .    What URL would get this function called?

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


def dq_and_do_cmds():
    msg, msgs = True, []
    while msg:
        msg = dq_and_do_one_cmd()
        msgs.append(msg)
    return msgs[:-1]  # Last item appended will be None

def dq_admin():
    msg, msgs = True, []
    while msg:
        msg = saveget.get_one_sqs_admin()
        msgs.append(msg)
    return msgs[:-1]  # Last item appended will be None


def instructions_view(request):
    return render(request, 'home.html')


def tickles(request):
    data = {'cmds': dq_and_do_cmds(), 'admins': dq_admin()}
    return HttpResponse(content=json.dumps(data))


