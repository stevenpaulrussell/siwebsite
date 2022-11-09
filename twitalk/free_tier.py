from django.http import HttpResponse

from filer import views as filerviews
from filer import twilio_cmds as twilio_cmds


# Processing of mms and voice call when the sender is established in free_tier
def mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel):
    from_tel_msg = None

    if not image_url and text == 'help':
        from_tel_msg = 'help message and http link'

    elif not image_url and text != 'help':
        filerviews.nq_cmd(from_tel, to_tel, cmd='cmd_general', text=text)
        from_tel_msg = 'Your command <{text}> is queued for processing... you will hear back!'

    elif image_url and text == 'profile':
        filerviews.nq_cmd(from_tel, to_tel, cmd='profile', image_url=image_url)
        from_tel_msg = 'You will be notified shortly, when your profile has been updated.'

    elif image_url and not text:
        wip = filerviews.load_wip(from_tel, to_tel)
        wip.update(dict(image_url=image_url, image_timestamp=timestamp))  
        filerviews.save_wip(from_tel, to_tel, wip)
        from_tel_msg = 'Good image received free tier'

    else:
       assert(not 'Error catch')
    return from_tel_msg


def recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata):
    from_tel_msg = None
    wip = filerviews.load_wip(from_tel, to_tel)

    # Update below to use the free_tier_morsel.  Also, get all the real stuff out of this in-line system
    if 'image_url' in wip:
        if 'RecordingUrl' in postdata:
            audio_url = postdata['RecordingUrl'] + '.mp3' 
            wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
            filerviews.nq_postcard(from_tel, to_tel, wip)    # This call also deletes the wip
            from_tel_msg =  'free_tier postcard sent'
        else:
            spoken = 'free_tier recording announcement OK image' 
            from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
    # Update above to use the free_tier_morsel.  Also, get all the real stuff out of this in-line system

    else:  # 'image_url' not in postdata.  Guide the sender. But this is not a new sender, so notifiy admin?
        if 'RecordingUrl' in postdata:    # Ignore the recording... or send it out on the admin queus
            from_tel_msg = 'free_tier instruction link to instructions.'
        else:
            spoken = f'free_tier recording announcement without image'
            from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
    return from_tel_msg


