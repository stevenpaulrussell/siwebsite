"""
Does the postmaster work for sqs and also for browser-called commands.

def some_cmd(from_tel, to_tel, **msg):
    assert(msg['cmd'] == 'some_cmd')

"""
import time
from filer import views as filerviews


def sender_first_postcard(from_tel, to_tel, **msg):
    """
    Set up this new sender from profile_url and wip. 
    Fix up the twilio-visible data by adding the free_tier info then removing the new_sender entry.
    """
    # Check for and make sender 
    # Check for and make conn with None for pobox_uuid
    # Proceed as in 'new_postcard'


    
    
def new_postcard(from_tel, to_tel, **msg):
    """
    """
    # Make postcard uuid data structure and store
    # Store postcard_uuid in the right place

    
def make_a_key(from_tel, to_tel):
    """
        Request may come from twilio or from website
        f'keys_{from_tel}':
        key -> value, to_tel -> to_tel, expire -> time.time of expiration
    """
    # Make and store a key
    # Where is the cleaner function that removes expired keys, new_senders?

    
def make_a_viewer(from_tel, key):
    """find the to_tel if any and check validity.
    If valid, ...pobox??
    """
    # Check for existing pobox, make new if needed.
    # Send announcement to all senders on pobox of new viewer.

    

def connect_a_sender():
    """
    Make this better
    Include possible recipient_name and key_sender name as to:   from:
    """

    

def set_recipient_name():
    """
    """

    
    
def set_sender_name():
    """
    ss"""



    


    