""" Interact with twilio and with an AWS S3 bucket to write  postcards SQS and commands SQS.  No calls made.  Prototype for
possible move of this function to twilio functions using JavaScript."""

from calendar import c
import os
import time
import uuid

from twilio.rest import Client as twilioClient

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from filer import views as filerviews
from filer import exceptions as filerexceptions

from free_tier import mms_to_free_tier, recorder_to_free_tier
from new_sender import mms_from_new_sender, recorder_from_new_sender
from twilio_cmds import sms_back, sms_mgmt_message, nq_admin_message, nq_cmd, nq_postcard


DEFAULT_TWILIO_NUMBER = '+18326626430'


#  Entry points. A postcard is made by mms  ->accept_media<-  for the photo, and  voice call  ->twi_recorder<-  for the audio
@csrf_exempt
def accept_media(request):      # mms entry point, image only for now!!
    try:
        postdata = request.POST
        timestamp, from_tel, to_tel, text = extract_request_values(postdata)
        media_type = postdata.get('MediaContentType0', 'no_media/no_media').split('/')[0]
        if media_type not in ('image', 'no_media'):
            sms_back(from_tel, to_tel, message_key="""Send instructions, note error back to user""")
            nq_admin_message(message="""note issues to error SQS""")
        image_url = postdata.get('MediaUrl0', None)
        free_tier_morsel = filerviews.load_from_free_tier(from_tel, to_tel)   
        if free_tier_morsel:  
            return mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel)
        else:
            return mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url)
    except Exception as E:
        nq_admin_message(message="""note issues to error SQS""")
    return HttpResponse()

@csrf_exempt
def twi_recorder(request):      # voice recording entry point
    try:
        postdata = request.POST
        timestamp, from_tel, to_tel, text = extract_request_values(postdata)
        free_tier_morsel = filerviews.load_from_free_tier(from_tel, to_tel)  
        if free_tier_morsel:
            return recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)
        else:
            return recorder_from_new_sender(timestamp, from_tel, to_tel, postdata)
    except Exception as E:
        nq_admin_message(message="""note issues to error SQS""")

    assert('Doing HTTP responses for Record and for normal termination ok'==False)
    # return http_back_message  # 'Record' command or error to Twilio, else have audio in media_url
    # Get this from recorder_to_free_tier or  recorder_from_new_sender
           

def extract_request_values(postdata):
    from_tel = postdata['From']
    to_tel = postdata['To']
    timestamp = time.time() - float(postdata.get('test_timeshift', '0'))
    text = postdata.get('Body', '').lower().strip()
    return timestamp, from_tel, to_tel, text



