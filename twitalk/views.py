""" Interact with twilio and with an AWS S3 bucket to write  postcards SQS and commands SQS.  No calls made.  Prototype for
possible move of this function to twilio functions using JavaScript."""

import os
import time
import uuid

from twilio.rest import Client as twilioClient

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

DEFAULT_TWILIO_NUMBER = '+18326626430'


# Entry points to get media from Twilio
@csrf_exempt
def accept_media(request):      # mms entry point 
    """Return sms to sender via a twilio html protocol, responsive to sms or mms from sender via twilio.  
    The sms message declares success, next step, sender error, or program error.  Program errors are from 
    the try/except wrapper.   Program error sends a message via 'sms_to_some_sender'."""

    if request.method!='POST':
        return HttpResponse(status=405)
    try:
        sender, to_tel, time_stamp = get_state_setup(request.POST)
        message, text, media_type, media_hint, media_url = mmscleaner(request.POST)
        if not message:
            # New below to be coded or changed, including sender key value fields
            message = process_media(time_stamp, sender, to_tel, text, media_type, media_hint, media_url)  # Raises exception if NCD
        save_one_sender_state(sender)
        text_back_to_sender = f"{message} Your status: {sender['status']}"
        return HttpResponse(content=f"<Response><Message>{text_back_to_sender}</Message></Response>")  
    except Exception as E:
        if os.environ['TEST'] == 'True':
            raise
        message = f'Have a problem: "{repr(E)}". Contact Steve'
        sms_to_some_sender(message, '+16502196500')
        return HttpResponse(content=f"<Response><Message>{message}</Message></Response>")  

@csrf_exempt
def twi_recorder(request):      # voice recording entry point
    """Follow a twilio protocol to manage voice recording by twilio, and return sms to sender via twilio.  
    The sms message declares success, next step, or program error. Program errors are from 
    the try/except wrapper. The twilio protocol is managed in mydata.voice_cleaner.  Program errors are from 
    the try/except wrapper.   Program error sends a message via 'sms_to_some_sender'."""

    if request.method!='POST':
        return HttpResponse(status=405)

