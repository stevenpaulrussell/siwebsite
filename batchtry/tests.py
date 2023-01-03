
import os
import json

import requests
from django.test import TestCase

from twitalk import views

data_source = os.environ['POSTBOX_DATA_SOURCE']


class OneCmdTests(TestCase):
    def test_simple(self):
        data = dict(From='a from tel', To='a twilio number', Body='help')
        response = requests.post(f'{data_source}/twitalk/accept_media', data=(data))
        self.assertEqual(response.status_code, 200)
        print(f'response: {response.text}')

