"""Instructions and marketing web views.
    Tickles receiver to dq cmds and return admin messages"""


import os
import json

from django.shortcuts import render
from django.http.response import HttpResponse

from postoffice.cmds import interpret_one_cmd
from saveget import saveget
from filer import twilio_cmds


data_source = os.environ['POSTBOX_DATA_SOURCE']


def run_from_event_queue():
    event_list = []
    while True:
        event = saveget.get_one_sqs_event()
        if not event:
            break
        event_list.append(event)
        message = interpret_one_cmd(event)
        if message:
            from_tel = event['from_tel']
            to_tel = event['to_tel']
            twilio_cmds.sms_back(from_tel=from_tel, to_tel=to_tel, message_key=message)
    return event_list  


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


