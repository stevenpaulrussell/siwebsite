# State storage for twitalk. 
# 

# senders
"""
f'free_tier/{from_tel}':                # This written by postmaster, read by twitalk
    f'from_{from_tel}': -> sender name if key is present        # Use to customize sms to sender
    f'to_{to_tel}:  -> recipient name if key is present         # Use to customize sms to sender

f'new_sender/{from_tel}':               # This written by twitalk, read by twitalk, deleted by postmaster
        'begun_at': -> time.time()      # When first heard from.  Pruned by postmaster if not completed within xx hours     
        'finished_at': -> time.time()   # When profile received.  This allows twitalk to process a new postcard immediately      
        'to_tel': -> to_tel             # Freeze any new to_tel until postmaster rewrites to free_tier
        'next_step': -> one of bare_image, bare_audio, profile_image, free_tier     # Simplify code by specifying what is acceptable
        'image_url': -> image media_url
        'image_hint': -> image media_hint
        'audio_url': -> audio media_url
        'audio_hint': -> audio media_hint
        'profile_url': -> profile image media_url
        'profile_hint': -> profile image media_hint
"""

# wip     
"""
f'wip/{from_tel}__to__{to_tel}'    # Written, read, and deleted by twitalk for state store
    'image': 
        'post_time': -> time.time() when image stored in cards_in_progress 
        'media_hint': 
        'media_url':
    'audio': 
        'post_time': 
        'media_hint': 
        'media_url':       
"""

# command SQS.  Includes explicit commands from sms and implicit commands, for now only 'new_sender'
""" 
json with from_tel, to_tel, command string
"""

# postcard SQS
"""
json with from_tel, to_tel, image_url, image_hint, audio_url, audio_hint, time_stamp
"""