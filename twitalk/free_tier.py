import time
import uuid

from django.http import HttpResponse

from filer import views as filerviews
from filer import lines


# Processing of mms and voice call when the sender is established in free_tier
def mms_to_free_tier(timestamp, tel_id, svc_id, text, image_url, free_tier_morsel):
    """Provide something to sender immediately.  Intend to move this to Twilio jscript.  Minimal state lookup"""
    msg_keys = dict(tel_id=tel_id, svc_id=svc_id, timestamp=timestamp, text=text)
    tel_id_msg = None
    if 'help' in text:      # Send help no matter what
        tel_id_msg = lines.line('Free tier help: Link to instructions', **msg_keys)
        return tel_id_msg
    if image_url:  # Either a postcard image or a profile image. Nothing else is valid
        if not text:        
            wip = filerviews.load_wip(tel_id, svc_id)
            wip.update(dict(image_url=image_url, image_timestamp=timestamp))  
            filerviews.save_wip(tel_id, svc_id, wip)
            tel_id_msg = lines.line('Good image received free tier', **msg_keys)
        elif text == 'profile':   # Have cmd 'profile' with image_url, all ok
            filerviews.nq_event(tel_id, svc_id, event_type='profile', profile_url=image_url)
            tel_id_msg = lines.line('Your profile will be updated shortly, and you will be notified.', **msg_keys)
        else:
            msg = 'Free tier, could not interpret command <{text}> with image {image_url}.'
            tel_id_msg = lines.line(msg, **msg_keys)
            filerviews.nq_admin_message(msg)
        return tel_id_msg
    if text == 'passkey' and not image_url:         
        passkey = str(uuid.uuid4())[0:4]
        expire = time.time() + 24*60*60
        filerviews.nq_event(tel_id, svc_id, event_type='passkey', passkey=passkey, expire=expire)
        tel_id_msg = lines.line(f'Your passkey is "{passkey}", valid in a few minutes, lasting for a day!') 
        return tel_id_msg
    assert(text and not image_url)
    filerviews.nq_event(tel_id, svc_id, event_type='text_was_entered', text=text)
    tel_id_msg = lines.line('Your command <{text}> is queued for processing... you will hear back!', **msg_keys)
    return tel_id_msg


def recorder_to_free_tier(timestamp, tel_id, svc_id, free_tier_morsel, postdata):
    msg_keys = dict(tel_id=tel_id, svc_id=svc_id, timestamp=timestamp)
    tel_id_msg, from_name, to_name = None, '', ''
    wip = filerviews.load_wip(tel_id, svc_id)
    if svc_id in free_tier_morsel:
        context = free_tier_morsel['svc_id']['postbox_id'] or 'NoViewer'
        msg_keys['from_name'] = free_tier_morsel['svc_id']['from']
        msg_keys['to_name'] = free_tier_morsel['svc_id']['to']
    else:
        context = 'NewRecipientFirst'
    to_speak = lines.line(f'Hello, {from_name}. Tell your story about that image for {to_name}', **msg_keys)
    if 'image_url' in wip:
        if 'RecordingUrl' in postdata:
            audio_url = postdata['RecordingUrl'] + '.mp3' 
            wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
            filerviews.nq_postcard(tel_id, svc_id, wip=wip, context=context)    
            tel_id_msg = lines.line('free_tier postcard sent', **msg_keys)
        else:
            tel_id_msg =  f'<Say>{to_speak}</Say><Record maxLength="120"/>'
    else:  # 'image_url' not in postdata.  Guide the sender. But this is not a new sender, so notifiy admin?
        if 'RecordingUrl' in postdata:    # Ignore the recording... or send it out on the admin queus
            tel_id_msg = lines.line('free tier ask to call & make recording & link to instructions.', **msg_keys)
        else:
            spoken = lines.line('free_tier recording announcement without image', **msg_keys)
            # Update above to use the free_tier_morsel.  Also, get all the real stuff out of this in-line system
            tel_id_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
    return tel_id_msg


