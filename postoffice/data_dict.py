"""
f'sender/{tel_id}':
    'version': -> start at 1
    'tel_id': -> tel_id      
    'profile_url': ->
    'sender_moniker': -> default to tel_id derivation, change by text command
    'morsel': ->     
        [svc_id]: ->
            'sender_moniker': -> sender name if key 'from' is present
            'recipient_moniker': -> recipient name if key is present
            'have_viewer': -> False or 'HaveViewer'   

        
f'polink/polink_{tel_id, svc_id}':
    'version': -> start at 1
    'tel_id': -> tel_id
    'svc_id': -> svc_id
    'sender_moniker':  -> default to {tel_id}['from'], change by text command  
    'recipient_moniker': ->  default to 'kith or kin', change by text command       
    'profile_url': -> copied from sender when polink is created.  
    'pobox_id': -> pobox_id.  Use tel_id for postcards sent with no pobox_id
    'most_recent_arrival_timestamp': -> time_stamp       # Enable nudges and alarms
    'cardlist_played': -> [postcard_id,]        # queue, newest at -1
    'card_current': -> postcard_id              # card in_play, *** or None if just being initialized.
    'cardlist_unplayed': -> [postcard_id,]      # queue, newest at -1.  Often empty!


f'pobox/pobox_{pobox_id}':    
    'version': -> start at 1
    'pobox_id': pobox_id
    'key_operator': tel_id              
    'heard_from': -> time.time() of last check-in from player
    'played_a_card': -> time.time() of last postbox.played_it
    'viewer_data: -> 
        tel_id: ->
            'card_id': -> 
            'play_count' -> 
            'profile_url': -> 
            'image_url': -> 
            'audio_url': -> 
            'audio_duration': -> 
            'svc_id': -> svc_id

    
f'card/card_{postcard_id}':
    'version': -> start at 1
    'card_id':  -> card_id, 
    'play_count':  -> default 0, then updated from Recently_Played_Cards_V1 when archived  ---> change this?                                  
    'polink': (tel_id, svc_id)
    'sent_at': -> time.time() when made and stored in S3 and referenced in post_office  
    'image_url': 
    'audio_url': 
    'profile_url': ->        at time postcard was made!  Viewer may see something different
    'retired_at': -> time.time(), added when retired from viewer_data
    'pobox_id': -> added when retired from viewer_data 

    
f'passkey_{tel_id}':             
    'tel_id': -> tel_id
    'svc_id': -> svc_id
    'passkey': -> value
    'expire': -> time.time of expiration

"""
