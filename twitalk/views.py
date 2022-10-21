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

#  Entry points. A postcard is made by mms -> accept_media <- for the photo, and  voice call -> twi_recorder <- for the audio
@csrf_exempt
def accept_media(request):      # mms entry point, image only for now!!
    postdata = request.POST
    timestamp, from_tel, to_tel, text = extract_request_values(postdata)
    media_type = postdata.get('MediaContentType0', 'no_media/no_media').split('/')[0]
    if media_type not in ('image', 'no_media'):
        sms_back(to_tel, message="""Send instructions, note error back to user""", from_twilio='WHATEVER1')
        enqueue_admin_message(message="""note issues to error SQS""")
    image_url = postdata.get('MediaUrl0', None)
    free_tier_morsel = filerviews.load_from_free_tier(from_tel, to_tel)   
    if free_tier_morsel:
        mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel)
    else:
        return mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url)
            
@csrf_exempt
def twi_recorder(request):      # voice recording entry point
    postdata = request.POST
    timestamp, from_tel, to_tel, text = extract_request_values(postdata)
    free_tier_morsel = filerviews.load_from_free_tier(from_tel, to_tel)  
    if free_tier_morsel:
        recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)
    else:
        recorder_from_new_sender(timestamp, from_tel, to_tel, postdata)
           


# Processing of mms and voice call when the sender is established in free_tier
def mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel):
    if not image_url and text == 'help':
        sms_back(to_tel, message='help message and http link', from_twilio='WHATEVER1')
    elif not image_url and text != 'help':
        cmd_json = """Call command pre-processor. If it is help, send directly, otherwise appeal to postmaster"""
        enqueue_cmd(from_tel, cmd_json)
    elif image_url and text == 'profile':
        cmd_json = """Send profile command SQS pre-processor. """
        enqueue_cmd(from_tel, cmd_json)
    elif image_url and not text:
        wip = filerviews.load_wip(from_tel, to_tel)
        wip.update(dict(image_url=image_url, image_timestamp=timestamp))   
        """write wip back to filer"""   
        message = 'Good image received plus morsel stuff'  # How to write this using S3 and the free_tier_morsel?
        sms_back(to_tel, message, from_twilio='WHATEVER1')
    else:
        """programmer error"""

def recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata):
    wip = filerviews.load_wip(from_tel, to_tel)
    if 'RecordingUrl' not in postdata and 'image_url' not in wip:
        """Send twilio command ask for image via mms and to not record."""
    elif 'RecordingUrl' in postdata and 'image_url' not in wip:
        """Error condition"""
    elif 'RecordingUrl' not in postdata and 'image_url' in wip:
        """Send twilio command to record using free_tier_morsel if it exists"""
    elif 'RecordingUrl'  in postdata and 'image_url' in wip:
        audio_url = postdata['RecordingUrl'] + '.mp3' 
        wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
        """write wip back to filer"""   
    else:
        """programmer error"""



# Processing of mms and voice call for new senders, setting them up including the profile image.
def mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url):
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    wip = filerviews.load_wip(from_tel, to_tel)
    match expect:
        case 'image':
            if image_url and not text:
                wip['image_url'] = image_url
                wip['image_timestamp'] = timestamp
                """Save the wip using filer"""
                message = 'Good image received new_sender'  # How to write this using S3 ?
                sms_back(to_tel, message, from_twilio='WHATEVER1')
                message = """Got this new sender OK"""   # How to write this using S3 and the new_sender info?
                sms_mgmt_message(message, from_twilio='WHATEVER2')
            else:
                message =  """Send request for first image and link to instructions, maybe note issues to error SQS, note error back to user"""
                sms_back(to_tel, message, from_twilio='WHATEVER1')
                message = """This error message, some detail added aside from what is stored in S3"""
                enqueue_admin_message(message)
        case 'audio':
            message = """Send some instruction back to call the number, link to instructions."""
            sms_back(to_tel, message, from_twilio='WHATEVER1')
            message = """This error message, some detail added aside from what is stored in S3"""
            enqueue_admin_message(message)
        case 'profile':
            if image_url and text == 'profile':

                
                """Send new_sender_profile on SQS, send welcome message, 
                    update expect to 'new_sender_ready', clear wip """
            else:
                """Send instruction on profile and link to instructions.  Make an error SQS for mgmt??"""
        case 'new_sender_ready':
            """Put image into wip same as for free_tier"""
        case _:
            """Raise some error"""
    return

def recorder_from_new_sender(timestamp, from_tel, to_tel, postdata):
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    audio_url = postdata.get('RecordingUrl', None)
    wip = filerviews.load_wip(from_tel, to_tel)
    match expect:
        case 'audio':
            if audio_url:
                audio_url = audio_url + '.mp3' 
                """Write the postcard sent SQS and clear the wip"""
            elif not audio_url:
                """Make the recording prompt using the from and to parameters if they exist."""
        case 'new_sender_ready':
            """Put image into wip same as for free_tier"""
        case _:    
            if audio_url:
                """Send sms to from_tel with instructions"""
            else:      
                """Play greeting to caller that says 'will send instructions'. """


def extract_request_values(postdata):
    from_tel = postdata['From']
    to_tel = postdata['To']
    timestamp = time.time() - float(postdata.get('test_timeshift', '0'))
    text = postdata.get('Body', '').lower().strip()
    return timestamp, from_tel, to_tel, text



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


def update_wip(wip, key_values):
    wip = wip.update(key_values)

def sms_back(to_tel, message, from_twilio='WHATEVER1'):
    """Use twilio to send text message to to_tel"""

def enqueue_postcard(from_tel, to_tel, wip):
    """Build and sqs message, call filer to send it, call filer to remove the wip."""

def enqueue_cmd(from_tel, cmd_json):
        """Call filer to send it."""

def enqueue_admin_message(message):
        """Call filer to send it."""

def sms_mgmt_message(message, from_twilio='WHATEVER2'):
        """Use twilio to send text message to WHATEVER2"""
