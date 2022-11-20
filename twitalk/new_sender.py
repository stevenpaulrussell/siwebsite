from django.http import HttpResponse

from filer import views as filerviews
from filer import lines
from .free_tier import mms_to_free_tier, recorder_to_free_tier


# Processing of mms and voice call for new senders, setting them up including the profile image.
def mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url):
    from_tel_msg = None
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    wip = filerviews.load_wip(from_tel, to_tel)
    msg_keys = dict(from_tel=from_tel, to_tel=to_tel, timestamp=timestamp)

    # First check for text=='help' to return something specific to new sender asking for help

    match expect:
        case 'new_sender_ready':    # Handle as for free_tier
            from_tel_msg =  mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel={})

        case 'image':
            # The caller, twitalk.views, checks media type allowing only None or image
            if image_url and not text:
                wip.update(dict(image_url=image_url, image_timestamp=timestamp))   
                filerviews.save_wip(from_tel, to_tel, wip)
                filerviews.save_new_sender(from_tel=from_tel, expect='audio')
                filerviews.nq_admin_message(lines.line('New sender <{from_tel}>, image OK', **msg_keys))
                from_tel_msg = lines.line('New sender welcome: image recvd', **msg_keys)
            else:
                filerviews.nq_admin_message(lines.line('New sender <{from_tel}>, missing plain image.', **msg_keys))
                from_tel_msg = lines.line('New sender: Request first image & link to specific instructions', **msg_keys)

        case 'audio':
            from_tel_msg = lines.line('New sender ask to call & make recording & link to specific instructions.', **msg_keys)
            filerviews.nq_admin_message(lines.line('New sender <{from_tel}> error: expect audio, in mms', **msg_keys))

        case 'profile':
            if image_url and text == 'profile':
                filerviews.save_new_sender(from_tel=from_tel, expect='new_sender_ready')
                filerviews.nq_first_postcard(from_tel, to_tel, wip=wip, profile_url=image_url)  #This clears the wip
                from_tel_msg = lines.line('New sender complete welcome message', **msg_keys)
            else:
                from_tel_msg = lines.line('New sender profile instruction & link to specific instructions.', **msg_keys)
                filerviews.nq_admin_message(lines.line('New sender <{from_tel}> error: expect profile', **msg_keys))

        case _:
            raise Exception('some message')   # Should drive an immediate sms to mgmt as well as nq_admin
    return from_tel_msg


def recorder_from_new_sender(timestamp, from_tel, to_tel, postdata):
    from_tel_msg = None
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    msg_keys = dict(from_tel=from_tel, to_tel=to_tel, timestamp=timestamp)
    match expect:
        case 'new_sender_ready':
            free_tier_morsel = {}
            from_tel_msg = recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)

        case 'audio':
            wip = filerviews.load_wip(from_tel, to_tel)
            if 'RecordingUrl' not in postdata:
                spoken = lines.line('Hello, and welcome to the postcard system audio function. The system got your photo.  \
                            Now, record your story about that photo in two minutes or less. \
                            Then just hang up, and you will have made your first postcard.', **msg_keys)
                from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
            else:
                audio_url = postdata['RecordingUrl'] + '.mp3' 
                wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
                filerviews.save_new_sender(from_tel, expect='profile')
                filerviews.save_wip(from_tel, to_tel, wip) 
                from_tel_msg = lines.line('Congrats to new sender making a first postcard.', **msg_keys)
        case _:    
            if 'RecordingUrl' not in postdata:
                spoken = lines.line('Hello! Welcome to the postcard system audio function. \
                            To use this, please text the system an image first. \
                            The system will text you instructions when you hang up.', **msg_keys)
                from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
                filerviews.nq_admin_message(lines.line('New sender unexpected call to twilio.', **msg_keys))
            else:
                from_tel_msg = lines.line('New sender instructions link on unexpected call to twilio.', **msg_keys)
    return from_tel_msg


