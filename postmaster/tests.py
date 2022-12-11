import time

from django.test import TestCase

from filer import views as filerviews 
from twitalk.tests import SiWebCarepostUser
from . import postcards, connects, saveget


class PostcardProcessing(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.sender_mobile_number = '+1_sender_mobile_number'
        self.twilio_phone_number = 'twilio_number_1'
        self.profile_url = 'sender_selfie_url'

    def test_create_new_sender(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        self.assertEqual(sender['version'], 1)
        self.assertEqual(sender['conn'], {})

    def test_create_new_connection(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        postcards.create_new_connection(sender, self.twilio_phone_number)
        conns = sender['conn']
        self.assertEqual(conns[self.twilio_phone_number]['to'], 'kith or kin')
        self.assertEqual(conns[self.twilio_phone_number]['pobox_id'], None)

    def test_make_morsel_no_postbox(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        postcards.create_new_connection(sender, self.twilio_phone_number)
        morsel = saveget.make_morsel(sender)
        self.assertEqual(morsel[self.twilio_phone_number]['from'], 'm b e r')
        self.assertEqual(morsel[self.twilio_phone_number]['to'], 'kith or kin')
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], False)
        
    def test_make_morsel_have_postbox(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        postcards.create_new_connection(sender, self.twilio_phone_number)
        sender['conn'][self.twilio_phone_number]['pobox_id'] = 'postbox_123'
        morsel = saveget.make_morsel(sender)
        self.assertEqual(morsel[self.twilio_phone_number]['from'], 'm b e r')
        self.assertEqual(morsel[self.twilio_phone_number]['to'], 'kith or kin')
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], 'HaveViewer')
    
    def test_create_postcard_update_sender(self):
        test_time = time.time()
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        postcards.create_new_connection(sender, self.twilio_phone_number)
        wip = dict(image_timestamp=test_time - 1, image_url='image_url',
                    audio_timestamp=test_time - 1, audio_url='audio_url')
        card = postcards.create_postcard_update_sender(sender, from_tel=self.sender_mobile_number,
                            to_tel=self.twilio_phone_number, wip=wip, sent_at=test_time)
        self.assertEqual(card['card_id'], sender['conn'][self.twilio_phone_number]['recent_card_id'])
        self.assertEqual(card['sent_at'], test_time)

# class HelperFunctionTests(TestCase):
#     def setUp(self):
#         filerviews.clear_the_read_bucket()
#         filerviews.clear_the_sqs_queue_TEST_SQS()
#         self.sender_mobile_number = '+1_sender_mobile_number'
#         self.twilio_phone_number = 'twilio_number_1'
#         self.profile_url = 'sender_selfie_url'

#     def test_get_passkey_when_absent(self):
#         passkey = connects.get_passkey(from_tel=self.sender_mobile_number)
#         self.assertIsNone(passkey)
   
#     def test_set_passkey_when_absent(self):
#         passkey = connects.set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number)
#         self.assertEqual(len(passkey), 4)
   
#     def test_get_passkey_when_present(self):
#         passkey1 = connects.set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number)
#         passkey2, to_tel = connects.get_passkey(from_tel=self.sender_mobile_number)
#         self.assertEqual(passkey1, passkey2)
#         self.assertEqual(to_tel, self.twilio_phone_number)
   
#     def test_get_passkey_when_expired(self):
#         passkey1 = connects.set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number, duration=-1)
#         passkey2 = connects.get_passkey(from_tel=self.sender_mobile_number)
#         self.assertEqual(len(passkey1), 4)
#         self.assertIsNone(passkey2)

#     def test_check_passkey_when_passing(self):
#         passkey = connects.set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number)
#         res = connects.check_passkey(self.sender_mobile_number, passkey)
#         self.assertIn('to_tel', res)
#         self.assertEqual(res['to_tel'], self.twilio_phone_number)
  
#     def test_check_passkey_when_no_match(self):
#         passkey = connects.set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number)
#         res = connects.check_passkey(self.sender_mobile_number, '1234')
#         self.assertNotIn('to_tel', res)
#         self.assertIn('error', res)
  
class NewPostcardCases(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.sender_mobile_number = '+1_sender_mobile_number'
        self.twilio_phone_number = 'twilio_number_1'
        self.profile_url = 'sender_selfie_url'
        self.wip = dict(image_timestamp='image_timestamp', image_url='image_url', 
                    audio_timestamp='audio_timestamp', audio_url='audio_url'
        )
        self.msg = dict(sent_at='sent_at', wip=self.wip)

    def test_new_postcard_newsenderfirst(self):
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        sender = saveget.get_sender(self.sender_mobile_number)
        morsel =  filerviews.load_from_free_tier(self.sender_mobile_number) 
        self.assertIn('conn', sender)
        self.assertEqual(sender['conn'][self.twilio_phone_number]['pobox_id'], None)
        self.assertIn(self.twilio_phone_number, morsel)
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], False)
        
    def test_connect_viewer_after_newsenderfirst(self):
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        sender = saveget.get_sender(self.sender_mobile_number)
        url_msg_string = connects.connect_viewer(sender, to_tel=self.twilio_phone_number)
        morsel =  filerviews.load_from_free_tier(self.sender_mobile_number) 
        self.assertIn(sender['conn'][self.twilio_phone_number]['pobox_id'], url_msg_string)
        self.assertIn(self.twilio_phone_number, morsel)
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], 'HaveViewer')
        
    def test_new_postcard_connect_viewer(self):
        # Setup and connect a sender to a viewer
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        sender = saveget.get_sender(self.sender_mobile_number)
        # Connect to a viewer
        connects.connect_viewer(sender, to_tel=self.twilio_phone_number)
        # See what happened
        pobox_id =  sender['conn'][self.twilio_phone_number]['pobox_id']
        pobox = saveget.get_pobox(pobox_id)
        cardlists = pobox['cardlists']
        viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertIn(self.sender_mobile_number, cardlists)
        self.assertEqual(len(cardlists[self.sender_mobile_number]), 1)
        self.assertIn(self.sender_mobile_number, viewer_data)

    def test_new_postcard_HaveViewer(self):
        # Setup and connect a sender to a viewer
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        sender = saveget.get_sender(self.sender_mobile_number)
        connects.connect_viewer(sender, to_tel=self.twilio_phone_number)
        # Send the test postcard
        specifics = dict(context='HaveViewer', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        # See what happened
        pobox_id =  sender['conn'][self.twilio_phone_number]['pobox_id']
        pobox = saveget.get_pobox(pobox_id)
        cardlists = pobox['cardlists']
        viewer_data = saveget.get_viewer_data(pobox_id)
        self.assertIn(self.sender_mobile_number, cardlists)
        self.assertEqual(len(cardlists[self.sender_mobile_number]), 2)
        self.assertIn(self.sender_mobile_number, viewer_data)
        self.assertEqual(cardlists[self.sender_mobile_number][0], viewer_data[self.sender_mobile_number]['card_id'])
        self.assertEqual(viewer_data[self.sender_mobile_number]['profile_url'], self.profile_url)

class ConnectCases(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.sender_mobile_number = '+1_sender_mobile_number'
        self.twilio_phone_number = 'twilio_number_1'
        self.profile_url = 'sender_selfie_url'
        self.wip = dict(image_timestamp='image_timestamp', image_url='image_url', 
                    audio_timestamp='audio_timestamp', audio_url='audio_url'
        )
        self.msg = dict(sent_at='sent_at', wip=self.wip)

    def test_disconnect_from_viewer(self):
        # Setup and connect a sender to a viewer
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        sender = saveget.get_sender(self.sender_mobile_number)
        # Connect to a viewer
        connects.connect_viewer(sender, to_tel=self.twilio_phone_number)
        # Disconnect from the viewer
        old_pobox_id =  sender['conn'][self.twilio_phone_number]['pobox_id']
        connects.disconnect_from_viewer(sender, self.twilio_phone_number)
        # See what happened
        pobox_id =  sender['conn'][self.twilio_phone_number]['pobox_id']
        self.assertIsNone(pobox_id)

