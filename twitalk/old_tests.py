from django.test import TestCase

from django.test import TestCase
from django.test.client import RequestFactory

from . import filer 
from .views import accept_media, twi_recorder

AUDIO = 'audio/ogg'
IMAGE = 'image/jpeg'

class CarepostUser:         
    to_0 = '+1twilio_test_phone_0'
    to_1 = '+1twilio_test_phone_1'
    url0 = 'media_url_0'
    url1 = 'media_url_1'
    url2 = 'media_url_2'

    def __init__(self, name, mobile_number=None) -> None:
        self.user_name = name
        self.user_mobile_number = mobile_number or f'{name}_+1mobile_number'

    def _set_twilio_key_values_one_media(self, **kwds):
        twilio_key_values = {'From': self.user_mobile_number, 'Body': '', 'NumMedia': 1}
        twilio_key_values.update(kwds)
        if twilio_key_values['test_time_shift']==None:
            twilio_key_values.pop('test_time_shift')
        return twilio_key_values

    def _set_twilio_key_values_zero_media(self, **kwds):
        twilio_key_values = {'From': self.user_mobile_number, 'Body': '', 'NumMedia': 0}
        twilio_key_values.update(kwds)
        if twilio_key_values['test_time_shift']==None:
            twilio_key_values.pop('test_time_shift')
        return twilio_key_values

    def make_media_request(self, media, To=to_0, MediaUrl0=url0, body='', test_time_shift=None):
        twilio_key_values = self._set_twilio_key_values_one_media(
            MediaContentType0=media, To=To, MediaUrl0=MediaUrl0, Body=body, test_time_shift=test_time_shift)
        request = RequestFactory().post('/postbox/', twilio_key_values)        
        response = accept_media(request)
        return response

    def make_twi_voice_recorder_start_request(self, To=to_0, RecordingUrl=url0, test_time_shift=None):
        twilio_key_values = {'From': self.user_mobile_number, 'To': To} 
        if test_time_shift:
            twilio_key_values['test_time_shift'] = test_time_shift          
        request = RequestFactory().post('/postbox/', twilio_key_values)        
        response = twi_recorder(request)
        return response

    def make_twi_recordering_done_request(self, To=to_0, RecordingUrl=url0, test_time_shift=None):
        twilio_key_values = {'From': self.user_mobile_number, 'To': To, 'RecordingUrl': RecordingUrl}
        if test_time_shift:
            twilio_key_values['test_time_shift'] = test_time_shift          
        request = RequestFactory().post('/postbox/', twilio_key_values)        
        response = twi_recorder(request)
        return response

    def make_text_only_request(self, body, To=to_0, test_time_shift=None):
        twilio_key_values = self._set_twilio_key_values_zero_media(Body=body, To=To, test_time_shift=test_time_shift)
        request = RequestFactory().post('/postbox/', twilio_key_values)        
        response = accept_media(request)
        return response


class ViewAcceptMediaErrorFromEstablishedSendersCaseTest(TestCase):
    def setUp(self) -> None:
        filer.clear_the_read_bucket()
        self.User1 = CarepostUser(name='user1')

    def test_accept_media_view_function_enforces_media_order(self):
        response = self.User1.make_media_request(media=AUDIO)
        self.assertIn('To begin, please send an image with no text', str(response.content))
        self.assertIn('Your status: starting', str(response.content))

    def test_accept_media_view_function_returns_proper_media_request(self):
        response = self.User1.make_media_request(media=IMAGE)
        self.assertIn('Welcome and good job!  Got the image, next send an audio', str(response.content))
        self.assertIn('Your status: need_audio', str(response.content))

    def xxxxxxxxxxxxxxxxxxxx_____test_have_got_boto3_exceptions_defined_for_new_sender_pbox_views_line_91(self):
        self.assertFalse('Handled boto3 exceptions')

class ViewAcceptMediaGoodPushCaseTest(TestCase):
    def setUp(self) -> None:
        filer.clear_the_read_bucket()
        self.User1 = CarepostUser(name='user1')

    def test_view_function_stores_first_good_image(self):
        self.User1.make_media_request(media=IMAGE)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        connections = sender['connections']
        image_piece = connections[CarepostUser.to_0]['wip']['image']
        self.assertIn('post_time', image_piece)
        self.assertEqual(image_piece['media_hint'], 'image/jpeg')
        self.assertEqual(image_piece['media_url'], CarepostUser.url0)
        self.assertEqual(sender['status'], 'need_audio')
    

class PostCardConstructorTests(TestCase):
    def setUp(self) -> None:
        filer.clear_the_read_bucket()
        self.User1 = CarepostUser(name='user1')

    def test_image_and_audio_make_a_postcard_and_clear_the_wip(self):
        image_resp = self.User1.make_media_request(media=IMAGE)
        completed_response = self.User1.make_media_request(media=AUDIO)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        connections = sender['connections']
        wip = connections[CarepostUser.to_0]['wip']
        self.assertIn('Got the image, next send an audio about it', str(image_resp.content))
        self.assertIn('next send an audio', str(image_resp.content))
        self.assertIn('You made your first postcard.  Finish by setting up the profile', str(completed_response.content))
        self.assertEqual(wip, {})


class Functional_NewSenderSignUpGoesToGettingAConnector(TestCase):
    def setUp(self) -> None:
        filer.clear_the_read_bucket()
        self.User1 = CarepostUser(name='user1')

    def test_new_sender_starts_by_sending_any_text(self):
        text_response = self.User1.make_text_only_request(body='whatever')
        self.assertEqual(text_response.status_code, 200)
        self.assertIn('To begin, please send an image with no text', str(text_response.content))

    def test_new_sender_send_image(self):
        image_resp = self.User1.make_media_request(media=IMAGE)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual(image_resp.status_code, 200)
        self.assertIn('Welcome and good job!  Got the image', str(image_resp.content))
        self.assertIn('Got the image, next send an audio about it', str(image_resp.content))
        self.assertEqual('need_audio', sender['status'])

    def test_new_sender_send_image_then_another_image(self):
        image_resp1 = self.User1.make_media_request(media=IMAGE)
        image_resp2 = self.User1.make_media_request(media=IMAGE)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual(image_resp2.status_code, 200)
        self.assertIn('To continue, please call this contact to leave your voice message', str(image_resp2.content))
        self.assertEqual('need_audio', sender['status'])

    def test_new_sender_send_image_then_webaudio(self):
        self.User1.make_media_request(media=IMAGE)
        audio_resp = self.User1.make_media_request(media=AUDIO)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual('need_profile', sender['status'])
        self.assertIn('Send a selfie with the text command, "profile".', str(audio_resp.content))

    def test_new_sender_send_image_then_audio_then_text(self):
        self.User1.make_media_request(media=IMAGE)
        self.User1.make_media_request(media=AUDIO)
        text_response = self.User1.make_text_only_request(body='whatever')
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual(text_response.status_code, 200)
        self.assertIn('Please send a selfie with the text command, "profile" to finish on-boarding', str(text_response.content))
        self.assertEqual('need_profile', sender['status'])

    def test_new_sender_send_image_then_web_audio_then_proper_profile(self):
        self.User1.make_media_request(media=IMAGE)
        self.User1.make_media_request(media=AUDIO)
        profile_response = self.User1.make_media_request(media=IMAGE, body='profile')
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        connections = sender['connections']
        self.assertIn('please go to https://dry-sierra-55179.herokuapp.com', str(profile_response.content))
        self.assertEqual(self.User1.user_mobile_number, sender['from_tel'])
        self.assertEqual(sender['status'], 'free_tier')
        self.assertIn('po_box_id', connections[CarepostUser.to_0])
        self.assertIn('recipient_handle', connections[CarepostUser.to_0])


class Functional_Postcards_And_Commands(TestCase):
    def setUp(self):
        filer.clear_the_read_bucket()
        self.User1 = CarepostUser(name='user1')
        self.enroll_user_to_free_tier(self.User1)

    def enroll_user_to_free_tier(self, aUser):
        aUser.make_media_request(media=IMAGE)
        aUser.make_media_request(media=AUDIO)
        aUser.make_media_request(media=IMAGE, body='profile')

    
    def test_signup_and_send_a_postcard(self):
        image_resp = self.User1.make_media_request(media=IMAGE)
        completed_response = self.User1.make_media_request(media=AUDIO)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        wip = sender['connections'][CarepostUser.to_0]['wip']
        self.assertIn('Got the image, next send an audio about it.', str(image_resp.content))
        self.assertIn('Postcard sent', str(completed_response.content))
        self.assertIn('Text the "to: <name>" command to use a name. Text "?" for help', str(completed_response.content))
        self.assertEqual(wip, {})
        
    def test_signup_and_send_non_command_text(self):
        text_response = self.User1.make_text_only_request(body='whatever')
        self.assertIn('Do not recognize commmand', str(text_response.content))

    def test_signup_and_send_proper_profile_command(self):
        command_profile_resp = self.User1.make_media_request(media=IMAGE, body='profile')
        self.assertIn('your profile image has been updated', str(command_profile_resp.content))

    def test_signup_and_send_from_command_to_set_a_name(self):
        set_a_name_response = self.User1.make_text_only_request(body='from: Steve')
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertIn('You will now be identified to others in your sending group by', str(set_a_name_response.content))
        self.assertEqual('steve', sender['name'])

    def test_view_function_replace_old_image_with_new_image_right_now(self):
        self.User1.make_media_request(media=IMAGE, MediaUrl0=CarepostUser.url0)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        image_piece_original = sender['connections'][CarepostUser.to_0]['wip']['image']
        replacement_response = self.User1.make_media_request(media=IMAGE, MediaUrl0=CarepostUser.url2)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        image_piece_replaced = sender['connections'][CarepostUser.to_0]['wip']['image']
        self.assertEqual(image_piece_original['media_url'], CarepostUser.url0)  
        self.assertEqual(image_piece_replaced['media_url'], CarepostUser.url2)  
        self.assertIn(' Got the image, next send an audio about it.', str(replacement_response.content))

    def test_connector_command(self):
        cmd_connector_resp = self.User1.make_text_only_request(body='connector')
        self.assertIn('Use connector ', str(cmd_connector_resp.content))
        self.assertIn(' to make postcard connection to viewers.', str(cmd_connector_resp.content))

    def test_improper_connection_command(self):
        cmd_connect_resp = self.User1.make_text_only_request(body='connect +15551212 connector a1b2')
        self.assertIn('Sorry, there is some problem with,', str(cmd_connect_resp.content))

    def test_proper_connect_command(self):
        self.User2 = CarepostUser(name='user2')   
        self.enroll_user_to_free_tier(self.User2)
        # find the connector and do the command
        sender2 = filer.load_one_sender_state(self.User2.user_mobile_number)
        sender2_po_box_id = sender2['connections'][CarepostUser.to_0]['po_box_id']
        connector = sender2_po_box_id[0:4]
        User1_cmd_to_connect_User2 = f'connect {self.User2.user_mobile_number} connector {connector}'
        cmd_resp = self.User1.make_text_only_request(body=User1_cmd_to_connect_User2)
        sender1 = filer.load_one_sender_state(self.User1.user_mobile_number)
        sender1_po_box_id = sender1['connections'][CarepostUser.to_0]['po_box_id']
        sender2 = filer.load_one_sender_state(self.User2.user_mobile_number)
        sender2_new_po_box_id = sender2['connections'][CarepostUser.to_0]['po_box_id']
        self.assertNotEqual(sender1_po_box_id, sender2_po_box_id)
        self.assertEqual(sender1_po_box_id, sender2_new_po_box_id)
        self.assertIn(f'Rerouted {self.User2.user_mobile_number} to send postcards to your recipient.', str(cmd_resp.content))

    def test_to_command_for_naming_recipients(self):
        sender_original = filer.load_one_sender_state(self.User1.user_mobile_number)
        to_command_reponse = self.User1.make_text_only_request(body='to: Gerry')
        sender_changed = filer.load_one_sender_state(self.User1.user_mobile_number)
        recipient_former = sender_original['connections'][CarepostUser.to_0]['recipient_handle']
        recipient_new = sender_changed['connections'][CarepostUser.to_0]['recipient_handle']
        self.assertIn(f'Renamed recipient {recipient_former} to {recipient_new}', str(to_command_reponse.content))
         

class Twilio_Recorder_Tests(TestCase):
    def setUp(self):
        filer.clear_the_read_bucket()
        self.User1 = CarepostUser(name='user1')

    def test_new_sender_send_image_then_calls_for_phone_recording(self):
        self.User1.make_media_request(media=IMAGE)
        twi_recorder_response = self.User1.make_twi_voice_recorder_start_request()
        self.assertEqual(twi_recorder_response.status_code, 200)
        self.assertIn('Now tell your story about it, then just hang up.', str(twi_recorder_response.content))
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual('need_audio', sender['status'])

    def test_new_sender_send_image_then_twilioaudio(self):
        self.User1.make_media_request(media=IMAGE)
        twi_recorder_response = self.User1.make_twi_recordering_done_request()
        self.assertEqual(twi_recorder_response.status_code, 200)
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual('need_profile', sender['status'])

    def test_new_sender_send_image_then_twilio_audio_then_proper_profile(self):
        self.User1.make_media_request(media=IMAGE)
        self.User1.make_twi_recordering_done_request()
        profile_response = self.User1.make_media_request(media=IMAGE, body='profile')
        sender = filer.load_one_sender_state(self.User1.user_mobile_number)
        self.assertEqual(profile_response.status_code, 200)
        self.assertEqual(sender['status'], 'free_tier')
        self.assertIn('please go to https://dry-sierra-55179.herokuapp.com', str(profile_response.content))

