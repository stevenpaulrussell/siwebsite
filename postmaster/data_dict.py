# postmaster data dictionary

"""
f'sender/{from_tel}':
    # {sender data structure}
    # conn?
    # most recent card (for each to_tel?)    'from_tel': from_tel
    'profile_photo_url': ->
    'name': -> default to from_tel, change by text command
    'heard_from': -> time.time() of last sms, mms, or twilio
    'connections':
        to_tel: 
            'wip': {}   #  'audio': -> dict(post_time=post_time, media_hint=media_hint, media_url=media_url)
                        #   'image': -> dict(post_time=post_time, media_hint=media_hint, media_url=media_url)
            'po_box_id': -> po_box_uuid  
            'recent_card_id': -> uuid4_card_id
            'recent_card_when': -> time_stamp
            'recipient_handle' -> default to to_tel, change by text command  



f'conn/{from_tel}/{to_tel}':
    pobox_uuid or None                          # None until viewer is connected for (from_tel, to_tel). 


f'pobox_{pobox_uuid}':
    key_operator: f'{from_tel}              # set when viewer is first connected for (from_tel, to_tel)
    'penpals': ->
        f'{from_tel}:   [postcard_uuid,]        # for each from_tel, a list of postcards not yet archived
    ...

    
    
f'card_{postcard_uuid}':
    # {postcard data structure}
        'uuid':  -> uuid4_card_id, 
        'plays':  -> default 0, then updated from Recently_Played_Cards_V1 when archived  ---> change this?                                  
        'addressing': 
            'from_tel':
            'to_tel': 
            'sent_at': -> time.time() when made and stored in S3 and referenced in post_office     
        'image_url': 
        'audio_url': 


    
f'keys_{from_tel}':
    key -> value, expire -> time.time of expiration

"""