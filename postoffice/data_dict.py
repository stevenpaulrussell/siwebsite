"""
f'sender/{from_tel}':
    'version': -> start at 1
    'from_tel': -> from_tel      
    'profile_url': ->
    'name_of_from_tel': -> default to from_tel derivation, change by text command
    'morsel': ->     
        [to_tel]: ->
            'name_of_from_tel': -> sender name if key 'from' is present
            'name_of_to_tel': -> recipient name if key is present
            'have_viewer': -> False or 'HaveViewer'   

        
f'correspondence/correspondence_{from_tel, to_tel}':
    'version': -> start at 1
    'name_of_from_tel':  -> default to {from_tel}['from'], change by text command  
    'name_of_to_tel': ->  default to 'kith or kin', change by text command       
    'profile_url': -> copied from sender when correspondence is created.  
    'pobox_id': -> pobox_id.  Use from_tel for postcards sent with no pobox_id
    'most_recent_arrival_timestamp': -> time_stamp       # Enable nudges and alarms
    'cardlist_played': -> [postcard_id,]        # queue, newest at -1
    'card_current': -> postcard_id              # card in_play, *** or None if just being initialized.
    'cardlist_unplayed': -> [postcard_id,]      # queue, newest at -1.  Often empty!


f'pobox/pobox_{pobox_id}':    
    'version': -> start at 1
    'pobox_id': pobox_id
    'key_operator': from_tel              
    'heard_from': -> time.time() of last check-in from player
    'played_a_card': -> time.time() of last postbox.played_it
    'box_flag': -> Boolean   
    'viewer_data: -> 
        from_tel:
            'card_id': -> 
            'play_count' -> 
            'profile_url': -> 
            'image_url': -> 
            'audio_url': -> 
            'audio_duration': -> 

    
f'card/card_{postcard_id}':
    'version': -> start at 1
    'card_id':  -> card_id, 
    'plays':  -> default 0, then updated from Recently_Played_Cards_V1 when archived  ---> change this?                                  
    'correspondence': (from_tel, to_tel)
    'sent_at': -> time.time() when made and stored in S3 and referenced in post_office  
    'image_url': 
    'audio_url': 
    'profile_url': ->        at time postcard was made!  Viewer may see something different
    'retired_at': -> time.time(), added when retired from viewer_data
    'pobox_id': -> added when retired from viewer_data 

    
f'passkey_{from_tel}':             
    'from_tel': -> from_tel
    'to_tel': -> to_tel
    'passkey': -> value
    'expire': -> time.time of expiration

"""
