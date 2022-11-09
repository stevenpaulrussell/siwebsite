# State storage for twitalk. 
# 

# senders
"""
f'free_tier/{from_tel}':                # These are written by postmaster, read by twitalk.
    f'{to_tel}':  
        'from': -> sender name if key 'from' is present        # Use to customize sms to sender
        'to': -> recipient name if key is present         # Use to customize sms to sender


f'new_sender/{from_tel}':               # Written and read, by twitalk and and deleted by postmaster
         -> image, audio, profile, new_sender_ready       

"""

# wip     
"""
f'wip/{from_tel}/{to_tel}':    `# Written, read, and deleted by twitalk for state store
    'image_timestamp': 
    'image_url':
    'audio_timestamp':          
    'audio_url':                
"""


# command SQS.  Includes explicit commands from sms and implicit commands, for now only 'new_sender'
""" 
....  json dict: from_tel:, to_tel:, cmd:, **message
cmd:
    profile
        image_url:

    new_postcard    
        wip:

    cmd_general
        text: 'text string..'
"""



# admin SQS
"""
string
"""