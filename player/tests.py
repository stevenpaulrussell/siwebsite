import json
import os
import time
import requests

from django.test import TestCase
from django.test.client import RequestFactory

from postoffice import cmds, connects
from postbox.views import return_playable_viewer_data
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




    def xtest_postbox_page_is_reachable(self):
        response = self.client.get('/player/postbox/test_box')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'read.html')
        self.assertIn('postcard_audio_id', str(response.content))




    def test_viewer_data_is_HTTP_fetchable(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        pobox_id = 'test_pobox'
        response = requests.get(f'{data_source}/player/viewer_data/{pobox_id}')
        self.assertEqual(response.status_code, 200)
        viewer_data = json.loads(response.content)
        self.assertIn('meta', viewer_data)

    def test_played_it_is_reachable(self):
        data_source = os.environ['POSTBOX_DATA_SOURCE']
        pobox_id = 'test_pobox'
        card_id = 'test_card_id'
        response = requests.get(f'{data_source}/player/played/{pobox_id}/{card_id}')
        test_return_message = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('test_pobox', test_return_message)



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
        cmds.interpret_one_event(Sender0.passkey('twil0'))
        sender0_passkey, to_tel_used = connects.get_passkey(Sender0.mobile)

        # Sender0 could use the passkey to get connected to the already established pobox
        # Check that the 'RPC' call from player.views.get_a_pobox_id would work!
        # Postponing running the 'validate_me' from player.views:  Dont know how to handle the form,
        #    and the untested part is small.
        expected_pobox_id = sender0['conn'][sender0_twil0]['pobox_id']
        redirect_response = requests.post(f'{data_source}/get_a_pobox_id', data={'from_tel': Sender0.mobile, 'passkey': sender0_passkey})
        redirected_url = redirect_response.url
        redirected_postbox_id =  redirected_url.split('/postbox/')[-1]
        self.assertEqual(redirect_response.status_code, 200)
        self.assertEqual(expected_pobox_id, redirected_postbox_id)

        # Run played_it and see that both postbox and view_data are updated
        # First check the current state
        pobox = saveget.get_pobox(expected_pobox_id)
        view_data = saveget.get_viewer_data(expected_pobox_id)
        pobox_card_list = pobox['cardlists'][Sender0.mobile]
        viewer_card_id = view_data[Sender0.mobile]['card_id']
        self.assertEqual(len(pobox_card_list), 1)
        pobox_card_id_before_play = pobox_card_list[0]

        # Now run played_it 
        response = requests.get(f'{data_source}/player/played/{expected_pobox_id}/{viewer_card_id}')
        # fetch the new state... but wait for state change to propogate S3!
        pobox = saveget.get_pobox(expected_pobox_id)
        view_data = saveget.get_viewer_data(expected_pobox_id)
        updated_pobox_card_list = pobox['cardlists'][Sender0.mobile]
        updated_viewer_card_id = view_data[Sender0.mobile]['card_id']
        retired_card = saveget.get_postcard(viewer_card_id)

        # Check that the played card id is gone,
        #  that view_data has the correct new card, and that the card is 'retired'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(updated_pobox_card_list), 0)
        self.assertEqual(updated_viewer_card_id, pobox_card_id_before_play)
        self.assertEqual(retired_card['pobox_id'], expected_pobox_id)
        self.assertIn('retired_at', retired_card)
        self.assertAlmostEqual(pobox['meta']['played_a_card'], time.time(), delta=10.)

        # Check that muliple plays works and that play_count is updated properly
        card = saveget.get_postcard(updated_viewer_card_id)
        self.assertEqual(card['play_count'], 0)
        response = requests.get(f'{data_source}/player/played/{expected_pobox_id}/{updated_viewer_card_id}')
        requests.get(f'{data_source}/player/played/{expected_pobox_id}/{updated_viewer_card_id}')
        requests.get(f'{data_source}/player/played/{expected_pobox_id}/{updated_viewer_card_id}')
        self.assertEqual(response.status_code, 200)


        card = saveget.get_postcard(updated_viewer_card_id)
        self.assertEqual(card['play_count'], 3)

        # Test that pobox.return_playable_viewer_data works fine, heard_from works
        response = requests.get(f'{data_source}/player/viewer_data/{expected_pobox_id}')
        pobox = saveget.get_pobox(expected_pobox_id)
        self.assertEqual(response.status_code, 200)
        view_data = json.loads(response.content)
        play_count_of_Sender0_card = view_data[Sender0.mobile]['play_count']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(play_count_of_Sender0_card, 3)
        self.assertAlmostEqual(pobox['meta']['heard_from'], time.time(), delta=10.)

       


