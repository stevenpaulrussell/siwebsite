# State storage for twitalk. 
# 

# senders
"""
f'free_tier/{from_tel}':                # These are written by postmaster, read by twitalk.
    f'{to_tel}':  
        'from': -> sender name if key 'from' is present        # Use to customize sms to sender
        'to': -> recipient name if key is present         # Use to customize sms to sender


f'new_sender/{from_tel}':               # These are written by postmaster, read by twitalk, deleted by postmaster
        'expect': -> image, audio, profile     # Simplify code by specifying what is acceptable

"""

# wip     
"""
f'wip/{from_tel}/{to_tel}'    # Written, read, and deleted by twitalk for state store
    'image_timestamp': 
    'image_url':
"""

# command SQS.  Includes explicit commands from sms and implicit commands, for now only 'new_sender'
""" 
json with from_tel, to_tel, command string
"""

# postcard SQS
"""
json with from_tel, to_tel, image_url, image_hint, audio_url, audio_hint, time_stamp
"""