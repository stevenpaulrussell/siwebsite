from django.test import TestCase

from filer import views as filerviews 

from twitalk.tests import SiWebCarepostUser

from . import postcards

class Postcard_commands(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.sender_mobile_number = '+1_sender_mobile_number'
        self.twilio_phone_number = 'twilio_number_1'
        self.profile_url = 'sender_selfie)_url'

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
        morsel = postcards.make_morsel(sender)
        self.assertEqual(morsel[self.twilio_phone_number]['from'], 'from_tel derived')
        self.assertEqual(morsel[self.twilio_phone_number]['to'], 'kith or kin')
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], False)
        
    def test_make_morsel_have_postbox(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        postcards.create_new_connection(sender, self.twilio_phone_number)
        sender['conn'][self.twilio_phone_number]['pobox_id'] = 'postbox_123'
        morsel = postcards.make_morsel(sender)
        self.assertEqual(morsel[self.twilio_phone_number]['from'], 'from_tel derived')
        self.assertEqual(morsel[self.twilio_phone_number]['to'], 'kith or kin')
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], True)
    
    def test_create_postcard_update_sender(self):
        pass
    
    def test_update_postbox_and_save(self):
        self.assertFalse('Still have postcards simple tests to write')
    
    