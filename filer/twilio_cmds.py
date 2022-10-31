import os

from django.http import HttpResponse 
from twilio.rest import Client as twilioClient


from . import lines

from .views import MGMT_TELEPHONE_NUMBER, DEFAULT_TWILIO_NUMBER 


def sms_back(from_tel, message_key, **kwds):
    """Use twilio to send text message to from_tel"""
    text_back_to_sender = lines.line(message_key, kwds)
    if os.environ['TEST'] == 'True':    
        """nq_admin_message(message) """
        pass
    else:
        """send to from_tel via twilio"""
        sms_to_some_telephone_number(text_back_to_sender, destination_number=from_tel)


def sms_mgmt_message(message_key, **kwds):
    """Use twilio to send text message to MGMT_TELEPHONE_NUMBER"""
    message = lines.line(message_key, kwds)
    if os.environ['TEST'] == 'True':    
        """nq_admin_message(message) """
        pass
    else:
        sms_to_some_telephone_number(message, destination_number=MGMT_TELEPHONE_NUMBER)


def twilio_answering_machine_announcement(message_key, free_tier_morsel=None):
    if free_tier_morsel:
        speak_to_sender = lines.line(message_key, free_tier_morsel)
        speak_to_sender = f'Hello {sender_name}. Have your photo.  Now tell your story about it, then just hang up.{sender_name}'
    else:
        speak_to_sender = f'Hello {sender_name}. Have your photo.  Now tell your story about it, then just hang up.{sender_name}'
    twilio_cmd = f'<Say>{speak_to_sender}</Say><Record maxLength="120"/>'
    return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{twilio_cmd}</Response>')


def sms_to_some_telephone_number(text_back_to_sender, destination_number, twilio_number=DEFAULT_TWILIO_NUMBER):
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = twilioClient(account_sid, auth_token)
        client.messages.create(to=destination_number, from_=twilio_number, body=text_back_to_sender)
