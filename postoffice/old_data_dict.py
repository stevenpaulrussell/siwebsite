# postmaster data dictionary

"""
f'sender/{tel_id}':
    'version': -> start at 1
    'tel_id' -> tel_id              # Serves as ID.  Make a uuid for the sender??
    'profile_url': ->
    'from': -> default to tel_id derivation, change by text command
    'heard_from': -> time.time() of last sms, mms, or twilio
    'conn':
        svc_id: 
            'from':  -> default to {tel_id}['from'], change by text command        # Used by twilio to customize sms to sender
            'to': ->  default to 'kith or kin', change by text command               # Used by twilio to customize sms to sender
            'pobox_id': -> pobox_id  or None                        # None until viewer is connected for (tel_id, svc_id). 
            'recent_card_id': -> card_id
            'recent_card_when': -> time_stamp



# CHANGED !
f'pobox/pobox_{pobox_id}':
    'meta':
        'version': -> start at 1
        'pobox_id': pobox_id
        'key_operator': tel_id              # set when viewer is first connected for (tel_id, svc_id)
        'heard_from': -> time.time() of last return_playable_viewer_data
        'played_a_card': -> time.time() of last postbox.played_it
    'cardlists':
        tel_id:   [postcard_id,]        # for each tel_id, a list of postcards not yet archived
    ...

    
    
f'card/card_{postcard_id}':
    'version': -> start at 1
    'card_id':  -> card_id, 
    'plays':  -> default 0, then updated from Recently_Played_Cards_V1 when archived  ---> change this?                                  
    'tel_id':
    'svc_id': 
    'sent_at': -> time.time() when made and stored in S3 and referenced in post_office  
    'image_url': 
    'audio_url': 
    'profile_url': ->        at time postcard was made!  Viewer may see something different
    'retired_at': -> time.time(), added when retired from viewer_data
    'pobox_id': -> added when retired from viewer_data 


    
f'passkey_{tel_id}':             # Used for 'connect' for security and to identify the svc_id and avoid having to type that.
    'tel_id': -> tel_id
    'svc_id': -> svc_id
    'passkey': -> value
    'expire': -> time.time of expiration


f'viewer_data_{pobox_id}':
    'meta':
        'version': -> 1
        'pobox_id': pobox_id
    tel_id:
        'card_id': -> 
        'play_count' -> 
        'profile_url': -> 
        'image_url': -> 
        'audio_url': -> 
        'audio_duration': -> 



"""