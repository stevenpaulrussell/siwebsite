
import os
import json
import time

from django.test import TestCase

from twitalk import free_tier

data_source = os.environ['POSTBOX_DATA_SOURCE']


class OneCmdTests(TestCase):
    def test_simple(self):
        data = dict(timestamp= time.time(), from_tel='from_tel', to_tel='to_tel', text='help', image_url='image_url', free_tier_morsel={})
        from_tel_msg = free_tier.mms_to_free_tier(**data)
        print(f'from_tel_msg: {from_tel_msg}')

