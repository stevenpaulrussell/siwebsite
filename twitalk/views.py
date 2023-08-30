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
from filer import lines

from .free_tier import mms_to_free_tier, recorder_to_free_tier
from .new_sender import mms_from_new_sender, recorder_from_new_sender


DEFAULT_TWILIO_NUMBER = '+18326626430'


#  Entry points. A postcard is made by mms  ->accept_media<-  for the photo, and  voice call  ->twi_recorder<-  for the audio
@csrf_exempt
def accept_media(request):      # mms entry point, image only for now!!
    tel_id_msg = None
    try:
        postdata = request.POST
        timestamp, tel_id, svc_id, text = extract_request_values(postdata)
        media_type = postdata.get('MediaContentType0', 'no_media/no_media').split('/')[0]
        if media_type not in ('image', 'no_media'):   
            tel_id_msg = lines.line('Send instructions for mms, got media <{media_type}>, expe', media_type=media_type)
            filerviews.nq_admin_message(message="""note issues to error SQS""")
        else:
            image_url = postdata.get('MediaUrl0', None)
            free_tier_morsel = filerviews.load_from_free_tier(tel_id)   
            if free_tier_morsel:  
                tel_id_msg =  mms_to_free_tier(timestamp, tel_id, svc_id, text, image_url, free_tier_morsel)
            else:
                tel_id_msg =  mms_from_new_sender(timestamp, tel_id, svc_id, text, image_url)
    except Exception as E:
        filerviews.nq_admin_message(message="""note issues to error SQS""")
        if os.environ['TEST'] == 'True': 
            raise
    assert(tel_id_msg)
    return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{tel_id_msg}</Response>')


@csrf_exempt
def twi_recorder(request):      # voice recording entry point
    tel_id_msg = None
    try:
        postdata = request.POST
        timestamp, tel_id, svc_id, text = extract_request_values(postdata)
        free_tier_morsel = filerviews.load_from_free_tier(tel_id)  
        if free_tier_morsel:
            tel_id_msg = recorder_to_free_tier(timestamp, tel_id, svc_id, free_tier_morsel, postdata)
        else:
            tel_id_msg = recorder_from_new_sender(timestamp, tel_id, svc_id, postdata)
    except Exception as E:
        filerviews.nq_admin_message(message="""note issues to error SQS""")
        if os.environ['TEST'] == 'True': 
            raise
    assert(tel_id_msg)
    return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{tel_id_msg}</Response>')
           

def extract_request_values(postdata):
    tel_id = postdata['From']
    svc_id = postdata['To']
    timestamp = time.time() - float(postdata.get('test_timeshift', '0'))
    text = postdata.get('Body', '').lower().strip()
    return timestamp, tel_id, svc_id, text



