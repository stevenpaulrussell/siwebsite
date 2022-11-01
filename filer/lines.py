import os
from tkinter import ALL

from .views import  ALL_MESSAGES


"""Supply standard text lines for sms messages and http.  Lines are read from aws.s3 so that the user experience can be
changed at S3 without recompiling.
For testing, the lines may be reflected version of the line name, so that UI changes do not force test changes.
The lines are read in at program load.  
"""

LINES = {}    # to be replaced by reading some item from S3.

def line(msg_key, **kwds):
    if os.environ['TEST'] == 'True':    
        return msg_key.format(**kwds) 
    else:
        """msg_key is the 'name' of the line, coming from some static file. """
        msg_frame = ALL_MESSAGES[msg_key]
        return msg_frame.format(**kwds)
