# postmaster data dictionary

"""
f'sender/{from_tel}':
    'version': -> start at 1
    'from_tel' -> from_tel              # Serves as ID.  Make a uuid for the sender??
    'profile_url': ->
    'heard_from': -> time.time() of last sms, mms, or twilio
    'conn':
        to_tel: 
            'from': -> -> default to from_tel, change by text command        # Used by twilio to customize sms to sender
            'to': ->  default to to_tel, change by text command               # Used by twilio to customize sms to sender
            'pobox_id': -> pobox_id  or None                        # None until viewer is connected for (from_tel, to_tel). 
            'recent_card_id': -> card_id
            'recent_card_when': -> time_stamp




f'pobox_{pobox_id}':
    'version': -> start at 1
    'id': pobox_id
    key_operator: f'{from_tel}              # set when viewer is first connected for (from_tel, to_tel)
    f'{from_tel}:   [postcard_id,]        # for each from_tel, a list of postcards not yet archived
    ...

    
    
f'card_{postcard_id}':
    'version': -> start at 1
    'id':  -> card_id, 
    'plays':  -> default 0, then updated from Recently_Played_Cards_V1 when archived  ---> change this?                                  
    'from_tel':
    'to_tel': 
    'sent_at': -> time.time() when made and stored in S3 and referenced in post_office     
    'image_url': 
    'audio_url': 
    'profile_url': ->        at time postcard was made!  Viewer may see something different


    
f'keys_{from_tel}':             # Used for 'connect' for security and to identify the to_tel and avoid having to type that.
    'version': -> start at 1
    'key': -> value
    'to_tel': ->
    'expire': -> time.time of expiration

"""