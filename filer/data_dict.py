# State storage for twitalk. 
# **********************************************************************
# 2023 August 4 Work Plan sketch --> Change 'command SQS' name and contents to 'event SQS and
# change the word 'cmd' to 'event' everywhere, including in functions. Change 'cmd_general' to 'text_was_entered'.
# 
# Then simplify and refactor the handling ... 
#
# **********************************************************************

# senders
"""
f'free_tier/{from_tel}':                # These are written by postmaster, read by twitalk.
    f'{to_tel}':  
        'from': -> sender name if key 'from' is present     # Use to customize sms to sender
        'to': -> recipient name if key is present           # Use to customize sms to sender
        'have_viewer': -> False or 'HaveViewer'             # Senders without <have_viewer> get cleared in 6 days (?)


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


# event SQS.  Includes explicit commands from sms and implicit commands, for now only 'new_sender'
""" 
....  json dict: from_tel:, to_tel:, event:, **message
event:
    first_postcard
        wip:
        profile_url:

    new_postcard    
        wip:

    profile:
        profile_url:

    cmd:
        text: 'text string..'
"""
# # command SQS.  Includes explicit commands from sms and implicit commands, for now only 'new_sender'
# """ 
# ....  json dict: from_tel:, to_tel:, cmd:, **message
# cmd:
#     first_postcard
#         wip:
#         profile_url:

#     new_postcard    
#         wip:

#     profile:
#         profile_url:

#     cmd_general
#         text: 'text string..'
# """



# admin SQS
"""
string
"""



# new_sender message keys
"""
new_sender
    from_tel_msg
        'New sender welcome: image recvd'
        'New sender: Request first image & link to instructions'
        'New sender ask to call & make recording & link to instructions.'
        'New sender complete welcome message'
        'New sender profile instruction & link to instructions.'
        'Congrats to new sender making a first postcard.'
        'New sender instructions link on unexpected call to twilio.'

    nq_admin_message
        'New sender <{from_tel}>, image OK' 
        'New sender <{from_tel}>, missing plain image.'
        'New sender <{from_tel}> error: expect audio, in mms'
        'New sender <{from_tel}> error: expect profile'
        'New sender unexpected call to twilio.'

    twilio speaks
        'Hello, and welcome to the postcard system audio function. The system got your photo.  \
                            Now, record your story about that photo in two minutes or less. \
                            Then just hang up, and you will have made your first postcard.'
        'Hello! Welcome to the postcard system audio function. \
                            To use this, please text the system an image first. \
                            The system will text you instructions when you hang up.'

"""
# free_tier message keys
"""
free_tier
    from_tel_msg
        'Free tier help: Link to instructions'
        'Your command <{text}> is queued for processing... you will hear back!'
        'Your profile will be updated shortly, and you will be notified.'
        'Good image received free tier'
        'free_tier postcard sent'
        'free tier ask to call & make recording & link to instructions.'

    nq_admin_message


    twilio speaks
        'free_tier recording announcement OK image'
        'free_tier recording announcement without image'

"""

# twitalk views message keys
"""


"""