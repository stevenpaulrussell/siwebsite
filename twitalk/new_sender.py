
from filer import views as filerviews
from filer.twilio_cmds import sms_back, sms_mgmt_message, twilio_answering_machine_announcement
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
                sms_back(from_tel, to_tel, message_key='Good image received new_sender', from_twilio='WHATEVER1')
                sms_mgmt_message(message='New sender sent image OK')
            else:
                sender_msg_key = 'New sender: Request first image. Also, link to instructions as second msg?'
                sms_back(from_tel, to_tel, message_key=sender_msg_key)
                message = f'Admin message new sender, From_tel: {from_tel}'
                filerviews.nq_admin_message(message)

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
    return


def recorder_from_new_sender(timestamp, from_tel, to_tel, postdata):
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    match expect:
        case 'new_sender_ready':
            free_tier_morsel = {}
            recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata)

        case 'audio':
            wip = filerviews.load_wip(from_tel, to_tel)
            if 'RecordingUrl' not in postdata:
                """Send twilio command to record for new_sender"""
            else :
                audio_url = postdata['RecordingUrl'] + '.mp3' 
                wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
                filerviews.save_new_sender(new_sender=from_tel, expects='profile')
                filerviews.save_wip(from_tel, to_tel, wip) 

        case _:    
            if 'RecordingUrl' not in postdata:
                """Send twilio command to not record and play Play greeting to caller that says 'will send instructions"""
                sms_back(from_tel, to_tel, message_key="""Send instruction link to instructions. """)


