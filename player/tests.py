import json
import os
import requests

from django.test import TestCase
from django.test.client import RequestFactory



class LookAtPagesAndViews(TestCase):
    def test_info_page_is_reachable(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_to_connect_page_is_reachable(self):
        response = self.client.get('/connect')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'to_connect.html')

    def xtest_postbox_page_is_reachable(self):
        response = self.client.get('/postbox/some_postbox_id')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read.html')
        self.assertIn('postcard_audio_id', str(response.content))

    def test_can_get_data_source_from_env(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        self.assertIn('localhost', data_source)       

    def test_viewer_data_is_HTTP_fetchable(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        response = requests.get(f'{data_source}/viewer_data/some_postbox_id')
        viewer_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('meta', viewer_data)

