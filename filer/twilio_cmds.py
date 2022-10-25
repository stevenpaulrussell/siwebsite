import os

from . import views 


def sms_back(from_tel, message, from_twilio='WHATEVER1'):
    """Use twilio to send text message to to_tel"""
    if os.environ['TEST'] == 'True':    
        pass



def sms_mgmt_message(message, from_twilio='WHATEVER2'):
    """Use twilio to send text message to WHATEVER2"""
    if os.environ['TEST'] == 'True':    
        pass



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


