import os

from django.http import HttpResponse 
from twilio.rest import Client as twilioClient


from . import lines

from .views import MGMT_TELEPHONE_NUMBER, DEFAULT_TWILIO_NUMBER
from .views import nq_admin_message 


def sms_back(tel_id, svc_id, message_key, **kwds):
    """Use twilio to send text message to tel_id"""
    if os.environ['TEST'] == 'True':    
        message = dict(tel_id=tel_id, svc_id=svc_id, message_key=message_key, kwds=kwds)
        nq_admin_message(message)   
    else:
        text_back_to_sender = lines.line(message_key, **kwds)
        sms_to_some_telephone_number(text_back_to_sender, destination_number=tel_id, twilio_number=svc_id)


def sms_mgmt_message(message):
    """Use twilio to send text message to MGMT_TELEPHONE_NUMBER"""
    if os.environ['TEST'] == 'True':    
        nq_admin_message(message)   
    else:
        sms_to_some_telephone_number(message, destination_number=MGMT_TELEPHONE_NUMBER)



def sms_to_some_telephone_number(text_back_to_sender, destination_number, twilio_number=DEFAULT_TWILIO_NUMBER):
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = twilioClient(account_sid, auth_token)
        client.messages.create(to=destination_number, from_=twilio_number, body=text_back_to_sender)
