"""Instructions and marketing web views.
    Tickles receiver to dq cmds and return admin messages"""


import os
import json

from django.shortcuts import render
from django.http.response import HttpResponse

from postoffice.cmds import dq_and_do_one_cmd
from saveget import saveget

data_source = os.environ['POSTBOX_DATA_SOURCE']


def run_from_event_queue():
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
    data = {'cmd_msgs': run_from_event_queue(), 'admin_msgs': dq_admin()}
    return HttpResponse(content=json.dumps(data))


