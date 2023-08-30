"""
f'sender/{tel_id}':
    'version': -> start at 1
    'tel_id': -> tel_id      
    'profile_url': ->
    'sender_moniker': -> default to {create_default_using_tel_id(tel_id)}
    'morsel': ->     
        [svc_id]: ->
            'sender_moniker': -> 
            'recipient_moniker': -> copy from boxlink at viewer_data update
            'have_viewer': -> False or 'HaveViewer'   

        
f'boxlink/boxlink_{tel_id, svc_id}':
    'version': -> start at 1
    'tel_id': -> tel_id
    'svc_id': -> svc_id
    'sender_moniker':  -> copied from sender  
    'recipient_moniker': ->  default to 'kith or kin'       
    'profile_url': -> copied from sender when boxlink is created.  
    'pobox_id': -> pobox_id.  default None
    'most_recent_arrival_timestamp': -> time_stamp       # Enable nudges and alarms
    'cardlist_played': -> [postcard_id,]        # queue, newest at -1
    'card_current': ->  postcard_id             # None at start 
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
    'boxlink': (tel_id, svc_id)
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
