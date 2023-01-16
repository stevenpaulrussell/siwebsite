import os

from .views import  ALL_MESSAGES


"""Supply standard text lines for sms messages and http.  Lines are read from aws.s3 so that the user experience can be
changed at S3 without recompiling.
For testing, the lines may be reflected version of the line name, so that UI changes do not force test changes.
The lines are read in at program load.  
"""


def line(msg_key, **kwds):
    if os.environ['TEST'] == 'True':   
        try:
            msg_frame = {}.get(msg_key, msg_key)
            return msg_key.format(**kwds) 
        except:
            print(f'error in lines. \nmsg_key: <{msg_key}>, kwds: <{kwds}>\n')
            raise
    else:
        """msg_key is the 'name' of the line, coming from some static file. """
        msg_frame = ALL_MESSAGES.get(msg_key, msg_key)
        return msg_frame.format(**kwds)
