# postmaster data dictionary

"""
f'sender/{from_tel}':
    'version': -> start at 1
    'from_tel' -> from_tel              # Serves as ID.  Make a uuid for the sender??
    'profile_url': ->
    'from': -> default to from_tel derivation, change by text command
    'heard_from': -> time.time() of last sms, mms, or twilio
    'conn':
        to_tel: 
            'from':  -> default to {from_tel}['from'], change by text command        # Used by twilio to customize sms to sender
            'to': ->  default to 'kith or kin', change by text command               # Used by twilio to customize sms to sender
            'pobox_id': -> pobox_id  or None                        # None until viewer is connected for (from_tel, to_tel). 
            'recent_card_id': -> card_id
            'recent_card_when': -> time_stamp



# CHANGED !
f'pobox_{pobox_id}':
    'meta':
        'version': -> start at 1
        'pobox_id': pobox_id
        'key_operator': from_tel              # set when viewer is first connected for (from_tel, to_tel)
        'heard_from': -> time.time() of last postbox.played_it or return_playable_viewer_data
    'cardlists':
        from_tel:   [postcard_id,]        # for each from_tel, a list of postcards not yet archived
    ...

    
    
f'card_{postcard_id}':
    'version': -> start at 1
    'card_id':  -> card_id, 
    'plays':  -> default 0, then updated from Recently_Played_Cards_V1 when archived  ---> change this?                                  
    'from_tel':
    'to_tel': 
    'sent_at': -> time.time() when made and stored in S3 and referenced in post_office  
    'recent_play': -> time.time() when last played
    'image_url': 
    'audio_url': 
    'profile_url': ->        at time postcard was made!  Viewer may see something different


    
f'passkey_{from_tel}':             # Used for 'connect' for security and to identify the to_tel and avoid having to type that.
    'from_tel': -> from_tel
    'to_tel': -> to_tel
    'passkey': -> value
    'expire': -> time.time of expiration


f'viewer_data_{pobox_id}':
    'meta':
        'version': -> 1
        'pobox_id': pobox_id
    from_tel:
        'card_id': -> 
        'play_count' -> 
        'profile_url': -> 
        'image_url': -> 
        'audio_url': -> 
        'audio_duration': -> 



"""