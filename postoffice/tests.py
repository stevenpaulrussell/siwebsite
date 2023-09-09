import time

from django.test import TestCase

from filer import views as filerviews 
from twitalk.tests import SiWebCarepostUser
from saveget import saveget
from siwebsite_project import utils_4_testing

from . import postcards, connects, views


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
        self.assertEqual(sender['sender_moniker'], 'm b e r')

    def test_create_new_boxlink(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        boxlink = postcards.create_new_boxlink_update_morsel(sender, self.twilio_phone_number)
        self.assertEqual(boxlink['recipient_moniker'], 'kith or kin')
        self.assertEqual(boxlink['card_current'], None)
        self.assertEqual(boxlink['cardlist_unplayed'], [])
        self.assertEqual(boxlink['pobox_id'], None)

    def test_make_morsel_no_postbox(self):
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        boxlink = postcards.create_new_boxlink_update_morsel(sender, self.twilio_phone_number)
        #  card_id='a first card'
        morsel = saveget.make_morsel(sender)
        self.assertEqual(morsel[self.twilio_phone_number]['sender_moniker'], 'm b e r')
        self.assertEqual(morsel[self.twilio_phone_number]['recipient_moniker'], 'kith or kin')
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], False)
        
    def test_create_postcard(self):
        test_time = time.time()
        sender = postcards.create_new_sender(self.sender_mobile_number, self.profile_url)
        wip = dict(image_timestamp=test_time - 1, image_url='image_url',
                    audio_timestamp=test_time - 1, audio_url='audio_url')
        card_id = postcards.create_postcard(sender, tel_id=self.sender_mobile_number,
                            svc_id=self.twilio_phone_number, wip=wip, sent_at=test_time)
        postcard = saveget.get_postcard(card_id)
        self.assertAlmostEqual(postcard['sent_at'], test_time)


class HelperFunctionTests(TestCase):
    def setUp(self):
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.sender_mobile_number = '+1_sender_mobile_number'
        self.twilio_phone_number = 'twilio_number_1'
        self.profile_url = 'sender_selfie_url'

    def test_get_passkey_when_absent(self):
        passkey__svc_id__tuple = connects.get_passkey(tel_id=self.sender_mobile_number)
        self.assertIsNone(passkey__svc_id__tuple)
      
    def test_get_passkey_when_present(self):
        connects._set_passkey(tel_id=self.sender_mobile_number, svc_id=self.twilio_phone_number)
        passkey, svc_id = connects.get_passkey(tel_id=self.sender_mobile_number)
        self.assertEqual(len(passkey), 4)
        self.assertEqual(svc_id, self.twilio_phone_number)
   
    def test_get_passkey_when_expired(self):
        connects._set_passkey(tel_id=self.sender_mobile_number, svc_id=self.twilio_phone_number, duration=-1)
        passkey__svc_id__tuple = connects.get_passkey(tel_id=self.sender_mobile_number)
        self.assertIsNone(passkey__svc_id__tuple)
    

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
        """First postcard from twitalk with new sender, run through new_postcard."""
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        # Did sender, morsel, and boxlink get written properly?
        sender = saveget.get_sender(self.sender_mobile_number)
        morsel =  filerviews.load_from_free_tier(self.sender_mobile_number) 
        boxlink = saveget.get_boxlink(self.sender_mobile_number, self.twilio_phone_number)    
        self.assertEqual(sender['morsel'], morsel)
        self.assertIsNone(boxlink['pobox_id'])
        self.assertIn(self.twilio_phone_number, morsel)
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], False)

    def test_connect_viewer_after_newsenderfirst(self):
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        boxlink = saveget.get_boxlink(self.sender_mobile_number, self.twilio_phone_number)    
        # card_lists before pobox made:
        cardlist_unplayed_before_pobox = boxlink['cardlist_unplayed'].copy()
        card_current_before_pobox = boxlink['card_current']
        pobox_id = views.new_pobox_id(boxlink)
        morsel =  filerviews.load_from_free_tier(self.sender_mobile_number) 
        boxlink = saveget.get_boxlink(self.sender_mobile_number, self.twilio_phone_number)        
        cardlist_unplayed = boxlink['cardlist_unplayed']
        card_current = boxlink['card_current']
        pobox = saveget.get_pobox(pobox_id)
        viewer_data = pobox['viewer_data']
        self.assertEqual(boxlink['pobox_id'], pobox_id)
        self.assertIn(self.twilio_phone_number, morsel)
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], 'HaveViewer')
        self.assertEqual(len(cardlist_unplayed_before_pobox), 1)
        self.assertIsNone(card_current_before_pobox)
        self.assertEqual(len(cardlist_unplayed), 0)
        self.assertEqual(card_current, cardlist_unplayed_before_pobox[0])
        self.assertIn(self.sender_mobile_number, viewer_data)    
        self.assertEqual(morsel[self.twilio_phone_number]['have_viewer'], 'HaveViewer')

    def test_new_postcard_HaveViewer(self):
        # Setup sender with first card, connect to a viewer, send a second card
        specifics = dict(context='NewSenderFirst', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        sender_begin = saveget.get_sender(self.sender_mobile_number)
        boxlink_begin = saveget.get_boxlink(self.sender_mobile_number, self.twilio_phone_number)        
        pobox_id = views.new_pobox_id(boxlink_begin)
        # Send a second postcard. This should now occupy cardlist_unplayed
        specifics = dict(context='HaveViewer', profile_url=self.profile_url)
        self.msg.update(specifics)
        postcards.new_postcard(self.sender_mobile_number, self.twilio_phone_number, self.msg)
        # See what happened
        boxlink = saveget.get_boxlink(self.sender_mobile_number, self.twilio_phone_number)        
        cardlist = boxlink['cardlist_unplayed']
        pobox = saveget.get_pobox(pobox_id)
        self.assertEqual(len(cardlist), 1)  # 2 cards sent, but the first is now in card_current


class ConnectCases(TestCase):
    def setUp(self):
        # clear out AWS bucket and queue
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        # reset New_Tests_Sender
        utils_4_testing.New_Tests_Sender.reset()
    
    def test_make_a_new_pobox(self):
        # First sender completes sign-up
        A_Sender = utils_4_testing.New_Tests_Sender()
        msg = dict(sent_at='sent_at', wip=A_Sender.new_card_wip(), context='NewSenderFirst', profile_url=A_Sender.profile_url)
        postcards.new_postcard(A_Sender.tel_id, A_Sender.svc_id, msg)
        # Connect to a viewer
        boxlink = saveget.get_boxlink(A_Sender.tel_id, A_Sender.svc_id)
        pobox_id = views.new_pobox_id(boxlink)
        pobox = saveget.get_pobox(pobox_id)
        viewer_data = pobox['viewer_data']
        self.assertIn(A_Sender.tel_id, viewer_data)
        self.assertEqual(viewer_data[A_Sender.tel_id]['profile_url'], A_Sender.profile_url)

    def test_second_new_sender_connect_to_existing_pobox(self):
        # First sender completes sign-up
        A_Sender = utils_4_testing.New_Tests_Sender()
        msg = dict(sent_at='sent_at', wip=A_Sender.new_card_wip(), context='NewSenderFirst', profile_url=A_Sender.profile_url)
        postcards.new_postcard(A_Sender.tel_id, A_Sender.svc_id, msg)
        boxlinkA = saveget.get_boxlink(A_Sender.tel_id, A_Sender.svc_id)
        pobox_id_A = views.new_pobox_id(boxlinkA)
        # Setup second sender
        B = utils_4_testing.New_Tests_Sender()
        msg = dict(sent_at='sent_at', wip=B.new_card_wip(), context='NewSenderFirst', profile_url=B.profile_url)
        postcards.new_postcard(B.tel_id, B.svc_id, msg)
        # connect B as requester...
        msg = connects._connect_joining_sender_to_lead_sender_pobox(A_Sender.tel_id, \
                                    A_Sender.svc_id, requesting_tel_id=B.tel_id, requester_svc_id=B.svc_id)
        pobox_A = saveget.get_pobox(pobox_id_A)
        viewer_data = pobox_A['viewer_data']
        new_boxlinkB = saveget.get_boxlink(B.tel_id, B.svc_id)
        self.assertEqual(pobox_id_A, new_boxlinkB['pobox_id'])
        self.assertIn('Successfully connected', msg)
        self.assertIn(B.tel_id, viewer_data)
        self.assertIsNone(viewer_data[B.tel_id]['card_id'])       # B's first card is not carried over
        self.assertIsNotNone(viewer_data[A_Sender.tel_id]['card_id'])    # A's first card was carried over

    def test_disconnect_from_one_pobox_connect_to_another_existing_pobox(self):
        # First sender completes sign-up
        A = utils_4_testing.New_Tests_Sender()
        msg = dict(sent_at='sent_at', wip=A.new_card_wip(), context='NewSenderFirst', profile_url=A.profile_url)
        postcards.new_postcard(A.tel_id, A.svc_id, msg)
        boxlinkA = saveget.get_boxlink(A.tel_id, A.svc_id)
        pobox_id_A = views.new_pobox_id(boxlinkA)
        # Repeat setting up second sender B
        B = utils_4_testing.New_Tests_Sender()
        msg = dict(sent_at='sent_at', wip=B.new_card_wip(), context='NewSenderFirst', profile_url=B.profile_url)
        B_card_id_0 =  postcards.new_postcard(B.tel_id, B.svc_id, msg)
        boxlinkB = saveget.get_boxlink(B.tel_id, B.svc_id)
        # Now setup a viewer and pobox for B
        pobox_id_B = views.new_pobox_id(boxlinkB)
        # Do a connect, but now the requester has a pobox 
        msg = connects._connect_joining_sender_to_lead_sender_pobox(A.tel_id, \
                                    A.svc_id, requesting_tel_id=B.tel_id, requester_svc_id=B.svc_id)
        morselB = saveget.get_sender(B.tel_id)['morsel'][B.svc_id] 
        # B sends a second card, now with 'HaveViewer' set as context by twitalk using morsel
        msg = dict(sent_at='sent_at', wip=B.new_card_wip(), context='HaveViewer', profile_url=B.profile_url)
        B_card_id_1 = postcards.new_postcard(B.tel_id, B.svc_id, msg)
        # Get the results!  A and B send to pobox_A, while pobox_B has no one sending to it.
        pobox_A = saveget.get_pobox(pobox_id_A)
        viewer_data_A = pobox_A['viewer_data']
        pobox_B = saveget.get_pobox(pobox_id_B)
        viewer_data_B = pobox_B['viewer_data']
        new_boxlinkB = saveget.get_boxlink(B.tel_id, B.svc_id)
        self.assertEqual(morselB['have_viewer'], 'HaveViewer')
        self.assertEqual(pobox_id_A, new_boxlinkB['pobox_id'])
        self.assertIn(A.tel_id, viewer_data_A)
        self.assertIn(B.tel_id, viewer_data_A)
        self.assertEqual({}, viewer_data_B)

    def test_finish_disconnect_of_old_pobox(self):
        self.assertFalse('connects.delete_requester_from_former_pobox still needs work')    
        
    def test_event_context(self):
        self.assertFalse('postcards.new_postcard eventcontext still needs work')