from django.http import HttpResponse

from filer import views as filerviews
from filer.twilio_cmds import sms_back
from .free_tier import mms_to_free_tier, recorder_to_free_tier


# Processing of mms and voice call for new senders, setting them up including the profile image.
def mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url):
    from_tel_msg = None
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    wip = filerviews.load_wip(from_tel, to_tel)
    match expect:
        case 'new_sender_ready':    # Handle as for free_tier
            from_tel_msg =  mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel={})

        case 'image':
            if image_url and not text:
                wip.update(dict(image_url=image_url, image_timestamp=timestamp))   
                filerviews.save_wip(from_tel, to_tel, wip)
                filerviews.save_new_sender(from_tel=from_tel, expect='audio')
                filerviews.nq_admin_message(f'New sender <{from_tel}>, image OK')
                from_tel_msg = 'New sender welcome image'
            else:
                filerviews.nq_admin_message(message=f'New sender <{from_tel}>, missing plain image.')
                from_tel_msg = 'New sender: Request first image. Also, link to instructions as second msg?'

        case 'audio':
            from_tel_msg = 'Send some instruction back to call the number, link to instructions.'
            filerviews.nq_admin_message('User action telemetry')

        case 'profile':
            if image_url and text == 'profile':
                filerviews.save_new_sender(new_sender=from_tel, expect='new_sender_ready')
                filerviews.nq_postcard(from_tel, to_tel, wip)   #This clears the wip
                filerviews.nq_cmd(cmd_json="""Send new_sender_profile on SQS""")
                from_tel_msg = 'message_key send welcome message'
            else:
                """ Make an error SQS for mgmt??"""
                from_tel_msg = 'Send instruction on profile and link to instructions.'

        case _:
            raise Exception('some message')   # Should drive an immediate sms to mgmt as well as nq_admin
    return from_tel_msg


def recorder_from_new_sender(timestamp, from_tel, to_tel, postdata):
    from_tel_msg = None
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    match expect:
        case 'new_sender_ready':
            free_tier_morsel = {}
            from_tel_msg = recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)

        case 'audio':
            wip = filerviews.load_wip(from_tel, to_tel)
            if 'RecordingUrl' not in postdata:
                spoken = f'Hello, and welcome to the postcard system audio function. The system got your photo.  \
                            Now, record your story about that photo in two minutes or less. \
                            Then just hang up, and you will have made your first postcard. '
                from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
            else:
                audio_url = postdata['RecordingUrl'] + '.mp3' 
                wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
                filerviews.save_new_sender(from_tel, expect='profile')
                filerviews.save_wip(from_tel, to_tel, wip) 
                from_tel_msg = 'Congrats to new sender making a first postcard.'
        case _:    
            if 'RecordingUrl' not in postdata:
                spoken = f'Hello! Welcome to the postcard system audio function. \
                            To use this, please text the system an image first. \
                            The system will text you instructions when you hang up. '
                from_tel_msg =  f'<Say>{spoken}</Say><Record maxLength="120"/>'
            else:
                from_tel_msg = 'Send instruction link to instructions.'
    return from_tel_msg


