import json
import os
import requests

from django.test import TestCase
from django.test.client import RequestFactory

from postoffice import cmds, connects
from saveget import saveget

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
    def test_making_a_viewer_and_sending_played_it(self):
        """Sender0, Sender1 each have poboxes.  Sender1 is connected to Sender0 """
        # Set up
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        Sender0, Sender1 = run_simulation_of_two_senders()
        sender1_twil0 = Sender1.twi_directory['twil0']
        sender1_twil1 = Sender1.twi_directory['twil1']
        sender0_twil0 = Sender0.twi_directory['twil0']
        sender0 = saveget.get_sender(Sender0.mobile)

        # Sender0 gets a passkey (simulation, not testing twitalk)
        cmds.interpret_one_cmd(Sender0.passkey('twil0'))
        sender0_passkey, to_tel_used = connects.get_passkey(Sender0.mobile)

        # Sender0 could use the passkey to get connected to the already established pobox
        # Check that the 'RPC' call from player.views.get_a_pobox_id would work!
        # Postponing running the 'validate_me' from player.views:  Dont know how to handle the form,
        #    and the untested part is small.
        expected_pobox_id = sender0['conn'][sender0_twil0]['pobox_id']
        response = requests.get(f'{data_source}/validate_me/{Sender0.mobile}/{sender0_passkey}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected_pobox_id, json.loads(response.content))

        # Run played_it and see that both postbox and view_data are updated





