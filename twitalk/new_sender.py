from twilio_cmds import sms_back, sms_mgmt_message, nq_admin_message, nq_cmd, nq_postcard
from filer import views as filerviews
from free_tier import mms_to_free_tier, recorder_to_free_tier



# Processing of mms and voice call for new senders, setting them up including the profile image.
def mms_from_new_sender(timestamp, from_tel, to_tel, text, image_url):
    expect = filerviews.load_from_new_sender(from_tel)   # Postmaster will re-write the new_sender block
    wip = filerviews.load_wip(from_tel, to_tel)
    match expect:
        case 'image':
            if image_url and not text:
                wip.update(dict(image_url=image_url, image_timestamp=timestamp))   
                """Save the wip using filer"""
                message = 'Good image received new_sender'  # How to write this using S3 ?
                sms_back(from_tel, message, from_twilio='WHATEVER1')
                message = """Got this new sender OK"""   # How to write this using S3 and the new_sender info?
                sms_mgmt_message(message, from_twilio='WHATEVER2')
                """update expect to 'audio'"""
            else:
                message =  """Send request for first image and link to instructions, maybe note issues to error SQS, note error back to user"""
                sms_back(from_tel, message, from_twilio='WHATEVER1')
                message = """This error message, some detail added aside from what is stored in S3"""
                nq_admin_message(message)

        case 'audio':
            message = """Send some instruction back to call the number, link to instructions."""
            sms_back(from_tel, message, from_twilio='WHATEVER1')
            message = """This error message, some detail added aside from what is stored in S3"""
            nq_admin_message(message)

        case 'profile':
            if image_url and text == 'profile':
                nq_cmd(cmd_json="""Send new_sender_profile on SQS""")
                sms_back(from_tel, 'send welcome message')
                """update expect to 'new_sender_ready'"""
                nq_postcard(from_tel, to_tel, wip)   #This clears the wip
            else:
                """Send instruction on profile and link to instructions. """
                """ Make an error SQS for mgmt??"""

        case 'new_sender_ready':    # Handle as for free_tier
            mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel={})

        case _:
            sms_mgmt_message('programmer error')
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
                """update expect to 'profile'"""
                """write wip back to filer"""   

        case _:    
            if 'RecordingUrl' not in postdata:
                """Send twilio command to not record and play Play greeting to caller that says 'will send instructions"""
                """Send sms to from_tel with instructions"""

