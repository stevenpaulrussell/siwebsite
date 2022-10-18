""" Interact with twilio and with an AWS S3 bucket to write  postcards SQS and commands SQS.  No calls made.  Prototype for
possible move of this function to twilio functions using JavaScript."""

import os
import time
import uuid

from twilio.rest import Client as twilioClient

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from filer import views as filerviews
from filer import exceptions as filerexceptions

DEFAULT_TWILIO_NUMBER = '+18326626430'


# Entry points to get media from Twilio
@csrf_exempt
def accept_media(request):      # mms entry point, image only for now!!
    postdata = request.POST
    from_tel = postdata['From']
    to_tel = postdata['To']
    timestamp = time.time() - float(postdata.get('test_timeshift', '0'))
    text = postdata.get('Body', '').lower().strip()
    media_type = postdata.get('MediaContentType0', 'no_media/no_media').split('/')[0]
    image_url = postdata['MediaUrl0'] if media_type == 'image' else None 
    sender, wip = filerviews.load_from_free_tier(from_tel, to_tel)
    if sender:
        if image_url and not text:
            """Put image into wip"""
        elif image_url and text == 'profile':
            """Send profile command SQS pre-processor"""
        elif not image_url and text:
            """Call command pre-processor. If it is help, send directly, otherwise appeal to postmaster"""
        return 
    else:
        expect = filerviews.load_from_new_senders(from_tel)   
        match expect:
            case 'image':
                if image_url and not text:
                    """Send new_sender_image on SQS"""
                else:
                    """Send request for first image and link to instructions.  Make an error SQS for mgmt??"""
            case 'audio':
                """Send some instruction back to call the number, link to instructions.   Make an error SQS for mgmt??"""
            case 'profile':
                if image_url and text == 'profile':
                    """Send new_sender_profile on SQS and send welcome message"""
                else:
                    """Send instruction on profile and link to instructions.  Make an error SQS for mgmt??"""
            case _:
                """Raise some error"""



@csrf_exempt
def twi_recorder(request):      # voice recording entry point
    """Follow a twilio protocol to manage voice recording by twilio, and return sms to sender via twilio.  
    The sms message declares success, next step, or program error. Program errors are from 
    the try/except wrapper. The twilio protocol is managed in mydata.voice_cleaner.  Program errors are from 
    the try/except wrapper.   Program error sends a message via 'sms_to_some_sender'."""
    postdata = request.POST
    from_tel = postdata['From']
    to_tel = postdata['To']
    timestamp = time.time() - float(postdata.get('test_timeshift', '0'))
    audio_url = postdata.get('RecordingUrl', None)
    if audio_url:
        audio_url = audio_url + '.mp3' 
    sender, wip = filerviews.load_from_free_tier(from_tel, to_tel)
    if sender:
        if  'image_url' in wip: 
            if not audio_url:
                """Make the recording prompt using the from and to parameters if they exist."""
            else:
                """Write the postcard sent SQS and clear the wip"""
        else:
            """ Handle both a prompt to send an image then call, and also a message back with instructions."""



    # if sender:
    #     if 'RecordingUrl' in postdata:  
    #         return None,  postdata['RecordingUrl'] + '.mp3'
    #     else:
    #         sender_name = None if '+1' in sender['name'] else sender['name'] 
    #         recipient_handle = sender['connections'][to_tel]['recipient_handle'] 
    #         if '+1' in recipient_handle:
    #             spoken = f'Hello {sender_name}. Have your photo.  Now tell your story about it, then just hang up.'
    #         else:
    #             spoken = f'Hello {sender_name}. Have your photo.  Now tell {recipient_handle} your story about it, then just hang up.'
    #         twilio_cmd = f'<Say>{spoken}</Say><Record maxLength="100"/>'
    #         return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{twilio_cmd}</Response>'), None


