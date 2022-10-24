import os

from . import views 

"""Supply standard text lines for sms messages and http.  Lines are read from aws.s3 so that the user experience can be
changed at S3 without recompiling.
For testing, the lines may be reflected version of the line name, so that UI changes do not force test changes.
The lines are read in at program load.  
"""

LINES = {}    # to be replaced by reading some item from S3.

def line(key, **kwds):
    """key is the 'name' of the line allowing retrieval.  'args' will be any additional parameters, such as To: or From:"""
    if os.environ['TEST'] == 'True':    
        return f'<{key} looked up> using {kwds}'