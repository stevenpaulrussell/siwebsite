from django.http import HttpResponse

from filer import views as filerviews
from filer import lines
from .free_tier import mms_to_free_tier, recorder_to_free_tier


# Processing of mms and voice call for new senders, setting them up including the profile image.
def mms_from_new_sender(timestamp, tel_id, svc_id, text, image_url):
    tel_id_msg = None
    expect = filerviews.load_from_new_sender(tel_id)   
    wip = filerviews.load_wip(tel_id, svc_id)
    msg_keys = dict(tel_id=tel_id, svc_id=svc_id, timestamp=timestamp)

    # First check for text=='help' to return something specific to new sender asking for help.  Write a test for this!!!

    match expect:
        case 'new_sender_ready':    # Handle as for free_tier
            tel_id_msg =  mms_to_free_tier(timestamp, tel_id, svc_id, text, image_url, free_tier_morsel={})

        case None:
            # New sender case.  New sender will be stored if image recvd with no text. Otherwise, just return instructions
            if image_url and not text:
                wip.update(dict(image_url=image_url, image_timestamp=timestamp))   
                filerviews.save_wip(tel_id, svc_id, wip)
                filerviews.save_new_sender(tel_id=tel_id, expect='audio')
                filerviews.nq_admin_message(lines.line('New sender <{tel_id}>, image OK', **msg_keys))
                tel_id_msg = lines.line('New sender welcome: image recvd', **msg_keys)
            else:
                filerviews.nq_admin_message(lines.line('New sender <{tel_id}>, missing plain image.', **msg_keys))
                tel_id_msg = lines.line('New sender: Request first image & link to specific instructions', **msg_keys)

        case 'audio':
            tel_id_msg = lines.line('New sender ask to call & make recording & link to specific instructions.', **msg_keys)
            filerviews.nq_admin_message(lines.line('New sender <{tel_id}> error: expect audio, in mms', **msg_keys))

        case 'profile':
            if image_url and text == 'profile':
                filerviews.save_new_sender(tel_id=tel_id, expect='new_sender_ready')
                filerviews.nq_postcard(tel_id, svc_id, wip=wip, \
                            profile_url=image_url, context='NewSenderFirst')          
                tel_id_msg = lines.line('New sender complete welcome message', **msg_keys)
            else:
                tel_id_msg = lines.line('New sender profile instruction & link to specific instructions.', **msg_keys)
                filerviews.nq_admin_message(lines.line('New sender <{tel_id}> error: expect profile', **msg_keys))

        case _:
            raise Exception('some message')   # Should drive an immediate sms to mgmt as well as nq_admin
    return tel_id_msg


def recorder_from_new_sender(timestamp, tel_id, svc_id, postdata):
    tel_id_msg = None
    expect = filerviews.load_from_new_sender(tel_id)   # Postmaster will re-write the new_sender block
    msg_keys = dict(tel_id=tel_id, svc_id=svc_id, timestamp=timestamp)
    match expect:
        case 'new_sender_ready':
            free_tier_morsel = {}
            tel_id_msg = recorder_to_free_tier(timestamp, tel_id, svc_id, free_tier_morsel, postdata)

        case 'audio':
            wip = filerviews.load_wip(tel_id, svc_id)
            if 'RecordingUrl' not in postdata:
                spoken = lines.line('Hello, and welcome to the postcard system audio function. The system got your photo.  \
                            Now, record your story about that photo in two minutes or less. \
                            Then just hang up, and you will have made your first postcard.', **msg_keys)
                tel_id_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
            else:
                audio_url = postdata['RecordingUrl'] + '.mp3' 
                wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
                filerviews.save_new_sender(tel_id, expect='profile')
                filerviews.save_wip(tel_id, svc_id, wip) 
                tel_id_msg = lines.line('Congrats to new sender making a first postcard.', **msg_keys)
        case _:    
            if 'RecordingUrl' not in postdata:
                spoken = lines.line('Hello! Welcome to the postcard system audio function. \
                            To use this, please text the system an image first. \
                            The system will text you instructions when you hang up.', **msg_keys)
                tel_id_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
                filerviews.nq_admin_message(lines.line('New sender unexpected call to twilio.', **msg_keys))
            else:
                tel_id_msg = lines.line('New sender instructions link on unexpected call to twilio.', **msg_keys)
    return tel_id_msg


