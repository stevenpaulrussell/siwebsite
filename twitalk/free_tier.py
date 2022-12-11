from django.http import HttpResponse

from filer import views as filerviews
from filer import lines


# Processing of mms and voice call when the sender is established in free_tier
def mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel):
    """Provide something to sender immediately.  Intend to move this to Twilio jscript.  Minimal state lookup"""
    msg_keys = dict(from_tel=from_tel, to_tel=to_tel, timestamp=timestamp, text=text)
    from_tel_msg = None
    if text == 'help':
        from_tel_msg = lines.line('Free tier help: Link to instructions', **msg_keys)
    elif image_url:
        if not text:
            wip = filerviews.load_wip(from_tel, to_tel)
            wip.update(dict(image_url=image_url, image_timestamp=timestamp))  
            filerviews.save_wip(from_tel, to_tel, wip)
            from_tel_msg = lines.line('Good image received free tier', **msg_keys)
        elif text == 'profile':   # Have cmd 'profile' with image_url, all ok
            filerviews.nq_cmd(from_tel, to_tel, cmd='profile', profile_url=image_url)
            from_tel_msg = lines.line('Your profile will be updated shortly, and you will be notified.', **msg_keys)
        else:
            msg = 'Free tier image with unimplemented command <{text}> received.'
            from_tel_msg = lines.line(msg, **msg_keys)
            filerviews.nq_admin_message(msg)
    else:  
        assert(text and not image_url)
        filerviews.nq_cmd(from_tel, to_tel, cmd='cmd_general', text=text)
        from_tel_msg = lines.line('Your command <{text}> is queued for processing... you will hear back!', **msg_keys)
    return from_tel_msg


def recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata):
    msg_keys = dict(from_tel=from_tel, to_tel=to_tel, timestamp=timestamp)
    from_tel_msg, from_name, to_name = None, '', ''
    wip = filerviews.load_wip(from_tel, to_tel)
    if to_tel in free_tier_morsel:
        context = free_tier_morsel['to_tel']['postbox_id'] or 'NoViewer'
        msg_keys['from_name'] = free_tier_morsel['to_tel']['from']
        msg_keys['to_name'] = free_tier_morsel['to_tel']['to']
    else:
        context = 'NewRecipientFirst'
    to_speak = lines.line(f'Hello, {from_name}. Tell your story about that image for {to_name}', **msg_keys)
    if 'image_url' in wip:
        if 'RecordingUrl' in postdata:
            audio_url = postdata['RecordingUrl'] + '.mp3' 
            wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
            filerviews.nq_postcard(from_tel, to_tel, wip=wip, context=context)    
            from_tel_msg = lines.line('free_tier postcard sent', **msg_keys)
        else:
            from_tel_msg =  f'<Say>{to_speak}</Say><Record maxLength="120"/>'
    else:  # 'image_url' not in postdata.  Guide the sender. But this is not a new sender, so notifiy admin?
        if 'RecordingUrl' in postdata:    # Ignore the recording... or send it out on the admin queus
            from_tel_msg = lines.line('free tier ask to call & make recording & link to instructions.', **msg_keys)
        else:
            spoken = lines.line('free_tier recording announcement without image', **msg_keys)
            # Update above to use the free_tier_morsel.  Also, get all the real stuff out of this in-line system
            from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
    return from_tel_msg


