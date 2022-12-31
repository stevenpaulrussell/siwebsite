import json
import os
import requests

from django.test import TestCase
from django.test.client import RequestFactory

from siwebsite_project.test_functional import run_simulation_of_two_senders



class LookAtPagesAndViews(TestCase):
    def test_info_page_is_reachable(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_get_a_pobox_id_page_is_reachable(self):
        response = self.client.get('/get_a_pobox_id')
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
        response = requests.get(f'{data_source}/viewer_data/test_pobox')
        viewer_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('meta', viewer_data)

class DevelopmentTestsOfPlayerLookingAtStateSimulationOfTwoSenders(TestCase):
    def test_some_stuff(self):
        Sender0, Sender1 = run_simulation_of_two_senders()

    def test_unit_postoffice_has_function_to_find_pobox_id_from_passkey(self):
        pass

    def test_good_form_submission_redirects_to_right_postbox(self):
        pass

    def test_bad_form_submission_redirects_to_different_page(self):
        pass

