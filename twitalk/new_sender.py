from django.http import HttpResponse

from filer import views as filerviews
from filer.twilio_cmds import sms_back
from .free_tier import mms_to_free_tier, recorder_to_free_tier


# Processing of mms and voice call for new senders, setting them up including the profile image.
def mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url):
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    wip = filerviews.load_wip(from_tel, to_tel)
    match expect:
        case 'new_sender_ready':    # Handle as for free_tier
            mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel={})

        case 'image':
            if image_url and not text:
                wip.update(dict(image_url=image_url, image_timestamp=timestamp))   
                filerviews.save_wip(from_tel, to_tel, wip)
                filerviews.save_new_sender(from_tel=from_tel, expects='audio')
                sms_back(from_tel, to_tel, message_key='New sender sends image')
                filerviews.nq_admin_message(f'New sender <{from_tel}>, image OK')
            else:
                sender_msg_key = 'New sender: Request first image. Also, link to instructions as second msg?'
                sms_back(from_tel, to_tel, message_key=sender_msg_key)
                filerviews.nq_admin_message(message=f'New sender <{from_tel}>, missing plain image.')

        case 'audio':
            sms_back(from_tel, to_tel, message_key="""Send some instruction back to call the number, link to instructions.""")
            message = """User action telemetry"""     
            filerviews.nq_admin_message(message)

        case 'profile':
            if image_url and text == 'profile':
                filerviews.save_new_sender(new_sender=from_tel, expects='new_sender_ready')
                filerviews.nq_postcard(from_tel, to_tel, wip)   #This clears the wip
                filerviews.nq_cmd(cmd_json="""Send new_sender_profile on SQS""")
                sms_back(from_tel, to_tel, message_key='send welcome message')
            else:
                sms_back(from_tel, to_tel, message_key="""Send instruction on profile and link to instructions. """)
                """ Make an error SQS for mgmt??"""

        case _:
            raise Exception('some message')   # Should drive an immediate sms to mgmt as well as nq_admin
    return HttpResponse()


def recorder_from_new_sender(timestamp, from_tel, to_tel, postdata):
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    match expect:
        case 'new_sender_ready':
            free_tier_morsel = {}
            recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)

        case 'audio':
            wip = filerviews.load_wip(from_tel, to_tel)
            if 'RecordingUrl' not in postdata:
                spoken = f'Hello, and welcome to the postcard system audio function. The system got your photo.  \
                            Now, record your story about that photo in two minutes or less. \
                            Then just hang up, and you will have made your first postcard. '
                twilio_cmd = f'<Say>{spoken}</Say><Record maxLength="120"/>'
                return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{twilio_cmd}</Response>')
            else :
                audio_url = postdata['RecordingUrl'] + '.mp3' 
                wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
                filerviews.save_new_sender(new_sender=from_tel, expects='profile')
                filerviews.save_wip(from_tel, to_tel, wip) 

        case _:    
            if 'RecordingUrl' not in postdata:
                """Send twilio command to not record and play Play greeting to caller that says 'will send instructions"""
                sms_back(from_tel, to_tel, message_key="""Send instruction link to instructions. """)


