from django.test import TestCase

from django.test.client import RequestFactory


import json

class LookAtPagesAndViews(TestCase):
    def test_info_page_is_reachable(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_to_connect_page_is_reachable(self):
        response = self.client.get('/connect')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'to_connect.html')
