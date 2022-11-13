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

from .free_tier import mms_to_free_tier, recorder_to_free_tier
from .new_sender import mms_from_new_sender, recorder_from_new_sender


DEFAULT_TWILIO_NUMBER = '+18326626430'


#  Entry points. A postcard is made by mms  ->accept_media<-  for the photo, and  voice call  ->twi_recorder<-  for the audio
@csrf_exempt
def accept_media(request):      # mms entry point, image only for now!!
    from_tel_msg = None
    try:
        postdata = request.POST
        timestamp, from_tel, to_tel, text = extract_request_values(postdata)
        media_type = postdata.get('MediaContentType0', 'no_media/no_media').split('/')[0]
        if media_type not in ('image', 'no_media'):
            from_tel_msg = 'Send instructions, note error back to user'
            filerviews.nq_admin_message(message="""note issues to error SQS""")
        else:
            image_url = postdata.get('MediaUrl0', None)
            free_tier_morsel = filerviews.load_from_free_tier(from_tel)   
            if free_tier_morsel:  
                from_tel_msg =  mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel)
            else:
                from_tel_msg =  mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url)
    except Exception as E:
        filerviews.nq_admin_message(message="""note issues to error SQS""")
        if os.environ['TEST'] == 'True': 
            raise E
    assert(from_tel_msg)
    return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{from_tel_msg}</Response>')


@csrf_exempt
def twi_recorder(request):      # voice recording entry point
    from_tel_msg = None
    try:
        postdata = request.POST
        timestamp, from_tel, to_tel, text = extract_request_values(postdata)
        free_tier_morsel = filerviews.load_from_free_tier(from_tel, to_tel)  
        if free_tier_morsel:
            from_tel_msg = recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)
        else:
            from_tel_msg = recorder_from_new_sender(timestamp, from_tel, to_tel, postdata)
    except Exception as E:
        filerviews.nq_admin_message(message="""note issues to error SQS""")
    assert(from_tel_msg)
    return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{from_tel_msg}</Response>')
           

def extract_request_values(postdata):
    from_tel = postdata['From']
    to_tel = postdata['To']
    timestamp = time.time() - float(postdata.get('test_timeshift', '0'))
    text = postdata.get('Body', '').lower().strip()
    return timestamp, from_tel, to_tel, text



