from django.http import HttpResponse

from filer import views as filerviews
from filer import twilio_cmds as twilio_cmds


# Processing of mms and voice call when the sender is established in free_tier
def mms_to_free_tier(timestamp, from_tel, to_tel, text, image_url, free_tier_morsel):
    if not image_url and text == 'help':
        twilio_cmds.sms_back(from_tel, to_tel, message_key='help message and http link')

    elif not image_url and text != 'help':
        filerviews.nq_cmd(from_tel, cmd_json="""Call command pre-processor""")

    elif image_url and text == 'profile':
        filerviews.nq_cmd(from_tel, cmd_json="""Send profile command SQS pre-processor. """)

    elif image_url and not text:
        wip = filerviews.load_wip(from_tel, to_tel)
        wip.update(dict(image_url=image_url, image_timestamp=timestamp))  
        filerviews.save_wip(from_tel, to_tel, wip)
        twilio_cmds.sms_back(from_tel, to_tel, message_key='Good image received plus morsel stuff')

    else:
       assert not 'Error catch'


def recorder_to_free_tier(timestamp, from_tel, to_tel, free_tier_morsel, postdata):
    wip = filerviews.load_wip(from_tel, to_tel)
    if 'RecordingUrl' not in postdata and 'image_url' not in wip:
        twilio_cmds.sms_back(from_tel, to_tel, message_key='ask for image via mms: help message and http link')

    elif 'RecordingUrl' in postdata and 'image_url' not in wip:  # Ignore the audio -- need an image!
        pass

    elif 'RecordingUrl' not in postdata and 'image_url' in wip:
        if '+1' in recipient_handle:
            spoken = f'Hello {sender_name}. Have your photo.  Now tell your story about it, then just hang up.'
        else:
            spoken = f'Hello {sender_name}. Have your photo.  Now tell {recipient_handle} your story about it, then just hang up.'
        twilio_cmd = f'<Say>{spoken}</Say><Record maxLength="100"/>'
        return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{twilio_cmd}</Response>')
        return twilio_cmds.twilio_answering_machine_announcement('message_key', free_tier_morsel)

    else:
        assert 'RecordingUrl'  in postdata and 'image_url' in wip  # Catch the exception at the entry point
        audio_url = postdata['RecordingUrl'] + '.mp3' 
        wip.update(dict(audio_url=audio_url, audio_timestamp=timestamp))   
        filerviews.nq_postcard(from_tel, to_tel, wip)    # This call also deletes the wip
        twilio_cmds.sms_back(from_tel, to_tel, message_key='postcard is sent .... use free_tier_morsel to personalize it.')


