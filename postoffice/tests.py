import time

from django.test import TestCase

from filer import views as filerviews 
from twitalk.tests import SiWebCarepostUser
from saveget import saveget

from . import postcards, connects


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
        card_id = postcards.create_postcard_update_sender(sender, from_tel=self.sender_mobile_number,
                            to_tel=self.twilio_phone_number, wip=wip, sent_at=test_time)
        self.assertEqual(card_id, sender['conn'][self.twilio_phone_number]['recent_card_id'])

class HelperFunctionTests(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.sender_mobile_number = '+1_sender_mobile_number'
        self.twilio_phone_number = 'twilio_number_1'
        self.profile_url = 'sender_selfie_url'

    def test_get_passkey_when_absent(self):
        passkey__to_tel__tuple = connects.get_passkey(from_tel=self.sender_mobile_number)
        self.assertIsNone(passkey__to_tel__tuple)
      
    def test_get_passkey_when_present(self):
        connects._set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number)
        passkey, to_tel = connects.get_passkey(from_tel=self.sender_mobile_number)
        self.assertEqual(len(passkey), 4)
        self.assertEqual(to_tel, self.twilio_phone_number)
   
    def test_get_passkey_when_expired(self):
        connects._set_passkey(from_tel=self.sender_mobile_number, to_tel=self.twilio_phone_number, duration=-1)
        passkey__to_tel__tuple = connects.get_passkey(from_tel=self.sender_mobile_number)
        self.assertIsNone(passkey__to_tel__tuple)
    

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
        self.assertIn('meta', viewer_data)    # viewer_data not updated until pobox is called!
        self.assertNotIn(self.sender_mobile_number, viewer_data)    # viewer_data not updated until pobox is called!

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
        self.assertIn('meta', viewer_data)    # viewer_data not updated until pobox is called!
        self.assertNotIn(self.sender_mobile_number, viewer_data)    # viewer_data not updated until pobox is called!

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

