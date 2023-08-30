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
f'free_tier/{tel_id}':                # These are written by postmaster, read by twitalk.
    f'{svc_id}':  
        'from': -> sender name if key 'from' is present     # Use to customize sms to sender
        'to': -> recipient name if key is present           # Use to customize sms to sender
        'have_viewer': -> False or 'HaveViewer'             # Senders without <have_viewer> get cleared in 6 days (?)


f'new_sender/{tel_id}':               # Written and read, by twitalk and and deleted by postmaster
         -> image, audio, profile, new_sender_ready       

"""

# wip     
"""
f'wip/{tel_id}/{svc_id}':    `# Written, read, and deleted by twitalk for state store
    'image_timestamp': 
    'image_url':
    'audio_timestamp':          
    'audio_url':                
"""


# event SQS.  Includes explicit commands from sms and implicit commands, for now only 'new_sender'
""" 
....  json dict: tel_id:, svc_id:, event:, **message
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
# ....  json dict: tel_id:, svc_id:, cmd:, **message
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
    tel_id_msg
        'New sender welcome: image recvd'
        'New sender: Request first image & link to instructions'
        'New sender ask to call & make recording & link to instructions.'
        'New sender complete welcome message'
        'New sender profile instruction & link to instructions.'
        'Congrats to new sender making a first postcard.'
        'New sender instructions link on unexpected call to twilio.'

    nq_admin_message
        'New sender <{tel_id}>, image OK' 
        'New sender <{tel_id}>, missing plain image.'
        'New sender <{tel_id}> error: expect audio, in mms'
        'New sender <{tel_id}> error: expect profile'
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
    tel_id_msg
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