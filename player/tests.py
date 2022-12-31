import json
import os
import requests

from django.test import TestCase
from django.test.client import RequestFactory

from siwebsite_project.test_functional import run_simulation_of_two_senders



class LookAtURLs(TestCase):
    """These test the URLs and that functions pointed to by the URLs return something"""

    def test_can_get_data_source_from_env(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        self.assertIn('localhost', data_source)       

    def test_info_page_is_reachable(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_connect_page_for_getting_a_pobox_id_is_reachable(self):
        response = self.client.get('/get_a_pobox_id')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'to_connect.html')

    def test_postbox_page_is_reachable(self):
        response = self.client.get('/postbox/test_box')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read.html')
        self.assertIn('postcard_audio_id', str(response.content))

    def test_viewer_data_is_HTTP_fetchable(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        pobox_id = 'test_pobox'
        response = requests.get(f'{data_source}/viewer_data/{pobox_id}')
        viewer_data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('meta', viewer_data)

    def test_played_it_is_reachable(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        pobox_id = 'test_pobox'
        card_id = 'test_card_id'
        response = requests.get(f'{data_source}/played/{pobox_id}/{card_id}')
        test_return_message = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('test_pobox', test_return_message)

    def test_validate_me_is_HTTP_fetchable(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        from_tel = 'test_from_tel'
        passkey = 'test_passkey'
        response = requests.get(f'{data_source}/validate_me/{from_tel}/{passkey}')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(json.loads(response.content))


class DevelopmentTestsOfPlayerLookingAtStateSimulationOfTwoSenders(TestCase):
    def xtest_some_stuff(self):
        """Sender0, Sender1 each have poboxes.  Sender1 is connected to Sender0 """
        Sender0, Sender1 = run_simulation_of_two_senders()
        response = requests.post(f'{data_source}/viewer_data/test_pobox')


    def test_unit_postoffice_has_function_to_find_pobox_id_from_passkey(self):
        pass

    def test_good_form_submission_redirects_to_right_postbox(self):
        pass

    def test_bad_form_submission_redirects_to_different_page(self):
        pass

