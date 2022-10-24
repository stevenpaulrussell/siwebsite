from twilio_cmds import sms_back, sms_mgmt_message, nq_admin_message, nq_cmd, nq_postcard
from filer import views as filerviews


# Processing of mms and voice call when the sender is established in free_tier
def mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel):
    if not image_url and text == 'help':
        sms_back(from_tel, message='help message and http link', from_twilio='WHATEVER1')

    elif not image_url and text != 'help':
        nq_cmd(from_tel, cmd_json="""Call command pre-processor""")

    elif image_url and text == 'profile':
        nq_cmd(from_tel, cmd_json="""Send profile command SQS pre-processor. """)

    elif image_url and not text:
        wip = filerviews.load_wip(from_tel, to_tel)
        wip.update(dict(image_url=image_url, image_timestamp=timestamp))  
        filerviews.save_wip(from_tel, to_tel, wip)
        sms_back(from_tel, message='Good image received plus morsel stuff', from_twilio='WHATEVER1')

    else:
       assert not 'Error catch'


def recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata):
    wip = filerviews.load_wip(from_tel, to_tel)
    if 'RecordingUrl' not in postdata and 'image_url' not in wip:
        """Send twilio command ask for image via mms and to not record."""

    elif 'RecordingUrl' in postdata and 'image_url' not in wip:  # Ignore the audio -- need an image!
        pass

    elif 'RecordingUrl' not in postdata and 'image_url' in wip:
        """Send twilio command to record using free_tier_morsel if it exists"""

    else:
        assert 'RecordingUrl'  in postdata and 'image_url' in wip  # Catch the exception at the entry point
        audio_url = postdata['RecordingUrl'] + '.mp3' 
        wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
        nq_postcard(from_tel, to_tel, wip)    # This call also deletes the wip
        sms_back(from_tel, 'postcard is sent .... use free_tier_morsel to personalize it.')


