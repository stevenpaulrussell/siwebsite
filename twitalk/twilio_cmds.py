    # if sender:
    #     if 'RecordingUrl' in postdata:  
    #         return None,  postdata['RecordingUrl'] + '.mp3'
    #     else:
    #         sender_name = None if '+1' in sender['name'] else sender['name'] 
    #         recipient_handle = sender['connections'][to_tel]['recipient_handle'] 
    #         if '+1' in recipient_handle:
    #             spoken = f'Hello {sender_name}. Have your photo.  Now tell your story about it, then just hang up.'
    #         else:
    #             spoken = f'Hello {sender_name}. Have your photo.  Now tell {recipient_handle} your story about it, then just hang up.'
    #         twilio_cmd = f'<Say>{spoken}</Say><Record maxLength="100"/>'
    #         return HttpResponse(content=f'<?xml version="1.0" encoding="UTF-8"?><Response>{twilio_cmd}</Response>'), None



def sms_back(from_tel, message, from_twilio='WHATEVER1'):
    """Use twilio to send text message to to_tel"""

def nq_postcard(from_tel, to_tel, wip):
    """Build and sqs message, call filer to send it, call filer to remove the wip."""

def nq_cmd(from_tel, cmd_json):
        """Call filer to send it."""

def nq_admin_message(message):
        """Call filer to send it."""

def sms_mgmt_message(message, from_twilio='WHATEVER2'):
        """Use twilio to send text message to WHATEVER2"""
