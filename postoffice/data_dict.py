# postmaster data dictionary

# Goal is making the connect process easier to read in code, so easier to maintain.  Also, make the dats structures more inspectable for migration

"""
f'sender/{from_tel}':
    'version': -> start at 1
    'from_tel': -> from_tel              # Serves as ID.  Make a uuid for the sender??
    'profile_url': ->
    'name_of_from_tel': -> default to from_tel derivation, change by text command
    'heard_from': -> time.time() of last sms, mms, or twilio
    'morsel': ->            # Goes to twilio program side.  Info dublicated here for easier updates
        [to_tel]: ->
            'name_of_from_tel': -> sender name if key 'from' is present     # Use to customize sms to sender
            'name_of_to_tel': -> recipient name if key is present           # Use to customize sms to sender
            'have_viewer': -> False or 'HaveViewer'             # Senders without <have_viewer> get cleared in 6 days (?)


        
f'correspondence/correspondence_{from_tel, to_tel}':
    'version': -> start at 1
    'name_of_from_tel':  -> default to {from_tel}['from'], change by text command        # Used by twilio to customize sms to sender
    'name_of_to_tel': ->  default to 'kith or kin', change by text command               # Used by twilio to customize sms to sender
    'pobox_id': -> pobox_id.  Use from_tel for postcards sent with no pobox_id
    'most_recent_arrival_timestamp': -> time_stamp       # Enable nudges and alarms
    'cardlist_played': -> [postcard_id,]    # queue, newest at -1
    'card_current': -> postcard_id      # card in_play, *** or None if just being initialized.
    'cardlist_unplayed': -> [postcard_id,]    # queue, newest at -1.  Often empty!


f'pobox/pobox_{pobox_id}':    # These boxes refer to streams holding all cards
    'version': -> start at 1
    'pobox_id': pobox_id
    'key_operator': from_tel              # set when viewer is first connected for (from_tel, to_tel)
    'heard_from': -> time.time() of last check-in from player
    'played_a_card': -> time.time() of last postbox.played_it
    'box_flag': -> Boolean      # Set on some state change, esp loading a new unplayed card.  Cleared when data is retrieved.
    'correspondence_list: -> [(from_tel, to_tel)]       # Increment by connects, decrement by viewdata updates

    
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

"""
****************   Flows   ******************



"""