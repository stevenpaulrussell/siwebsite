"""
Does the postmaster work for sqs and also for browser-called commands.

def some_cmd(from_tel, to_tel, **msg):
    assert(msg['cmd'] == 'some_cmd')

"""

from filer import views as filerviews


def sender_first_postcard(from_tel, to_tel, **msg):
    """
    Set up this new sender using profile. 
    Fix up the twilio-visible data by adding the free_tier info then removing the new_sender entry.
    """
    # Check for and make sender 
    # Check for and make conn with None for pobox_uuid
    # Proceed as in 'new_postcard'


def new_postcard(**msg):
    """
    """
    # Make postcard uuid data structure and store
    # Store postcard_uuid in the right place

    



    


    


    