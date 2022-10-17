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
def accept_media(request):      # mms entry point 
    postdata = request.POST
    from_tel = postdata['From']
    to_tel = postdata['To']
    time_stamp = time.time() - float(postdata.get('test_time_shift', '0'))
    text = postdata.get('Body', '').lower().strip()
    media_type = postdata.get('MediaContentType0', 'no_media/no_media').split('/')[0]
    media_url = postdata.get('MediaUrl0', None)

    sender = filerviews.load_from_free_tier(from_tel, to_tel)
    if sender:
        msg = process_free_tier(sender, request)
        return msg
    else:
        sender = filerviews.load_from_new_senders(from_tel)   # filerviews will write a new sender if one is not found!
        msg = process_new_sender(sender, request)
        return msg


def process_free_tier(sender, request):
    pass

def process_new_sender(sender, request):
    pass

    
 
    try: 
        
    except filerexceptions.S3KeyNotFound:
        sender = dict(status='need_image', begun_at=time_stamp, to_tel=to_tel)
        filerviews.save_new_sender_state(from_tel=from_tel, state=sender)
    status = sender['status']
    match status:
        case 'free_tier':
            pass
        case 'need_image':
            pass 
        case 'need_audio':
            pass 
        case 'need_profile':
            pass 
        case 'image_needed':
            pass 
        case 'image_needed':
            pass 





    if request.method!='POST':
        
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
    try:
        sender, to_tel, time_stamp = get_state_setup(request.POST)
        http_back, media_url = voice_cleaner(request.POST, to_tel, sender)
        if http_back:
            return http_back  # 'Record' prompt 
        else:
            message = process_media(time_stamp, sender, to_tel, '', 'audio', 'audio/mp3', media_url)
            save_one_sender_state(sender)
            sms_to_some_sender(message, sender['from_tel'], twilio_number=to_tel)
            return HttpResponse()
    except Exception as E:
        if os.environ['TEST'] == 'True':
            raise
        message = f'Have a voice twilio problem "{repr(E)}" with message from {sender["from_tel"]} to {to_tel}.'
        sms_to_some_sender(message, '+16502196500')
        return HttpResponse()  

def process_media(time_stamp, sender, to_tel, text, media_type, media_hint, media_url):
    if sender['status'] in ('free_tier', ) and not text:
        message = process_regular_postcard(time_stamp, sender, to_tel, media_type, media_hint, media_url)
        # if 'Postcard sent' in message:
        #     send_the_new_card(time_stamp, sender)  # Use saved postcard id to update po_box & save po_box
    elif sender['status'] in ('free_tier', ) and text:
        message = process_possible_command(time_stamp, sender, to_tel, text, media_type, media_hint, media_url)
    elif sender['status'] in ('starting', 'need_audio', 'need_profile'):     
        message = process_new_sender_media(time_stamp, sender, to_tel, text, media_type, media_hint, media_url)
    if not message:
        status = f'sender: {sender}\n, to_tel: {to_tel} text: {text} media_type: {media_type}\n'
        raise Exception(f'In process media(), have no message generated. State: {status}')
    return message

def get_state_setup(postdata):
    from_tel = postdata['From']
    to_tel = postdata['To']
    try:
        time_stamp = time.time() - float(postdata['test_time_shift'])
    except KeyError:
        time_stamp = time.time()
    try:
        sender = load_one_sender_state(from_tel)
    except:   # Catch some boto3 exception!!
        sender = new_sender(from_tel, time_stamp)
    new_recipient_check(from_tel, to_tel, sender)
    return  sender, to_tel, time_stamp

def new_sender(from_tel, time_stamp):
    sender = dict(from_tel=from_tel, status='starting', profile_photo_url=None, name=from_tel, heard_from=time_stamp, connections={})
    sms_to_some_sender(f'new_sender_check: {from_tel}', '+16502196500')
    return sender

def new_recipient_check(from_tel, to_tel, sender):
    if to_tel not in sender['connections']:    
        wip = {}
        po_box_id = str(uuid.uuid4())
        sender['connections'][to_tel] = dict(wip=wip, po_box_id=po_box_id, recipient_handle=to_tel) 
        penpals = {from_tel: []}   
        po_box = dict(po_box_id=po_box_id, penpals=penpals, key_operators=[from_tel,])
        save_one_po_box(po_box)
        sms_to_some_sender(f'{from_tel} using new recipient to_tel: {to_tel}', '+16502196500')

def sms_to_some_sender(text_back_to_sender, senders_tel, twilio_number=DEFAULT_TWILIO_NUMBER):
        if 'test' in senders_tel in twilio_number or os.environ['TEST'] == 'True':
            if 'Error' in text_back_to_sender:
                print(f'\n\nsms to {senders_tel}: {text_back_to_sender}\n\n')
        else:
            account_sid = os.environ['TWILIO_ACCOUNT_SID']
            auth_token = os.environ['TWILIO_AUTH_TOKEN']
            client = twilioClient(account_sid, auth_token)
            client.messages.create(to=senders_tel, from_=twilio_number, body=text_back_to_sender)


