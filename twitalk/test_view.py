from django.test import TestCase
from django.test.client import RequestFactory
from filer import views as filerviews

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

def get_all_sqs():
    # In Test, both admin and cmd sqs go to test_sqs.
    # This function reads the one sqs queue, and demuxes
    # messages based on structure
    admin_list = []
    cmd_list = []
    while True:
        msg = filerviews.get_an_sqs_message()
        if msg:
            cmd_list.append(msg)
        else:
            break
    while True:
        msg = filerviews.get_an_sqs_message(QueueUrl=filerviews.ADMIN_URL)
        if msg:
            admin_list.append(msg)
        else:
            break
    return admin_list, cmd_list



class ViewAcceptMedia_NewSendersCases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = CarepostUser(name='user1')

    def test_good_image_from_new_sender(self):
        response = self.User1.make_media_request(media=IMAGE)
        admin_list, cmd_list = get_all_sqs()
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        self.assertIn('New sender welcome: image recvd', str(response.content))
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(cmd_list), 0)
        self.assertEqual(expect, 'audio')

    def test_mms_rejects_audio_with_explanation(self):
        # This response  and admin msgs are generated immediately from accept_media
        response = self.User1.make_media_request(media=AUDIO)
        admin_list, cmd_list = get_all_sqs()
        admin_msg = admin_list[0]
        expected_admin_msg = 'note issues to error SQS'
        self.assertIn('Send instructions for mms, got media <audio>, ', str(response.content))
        self.assertEqual(expected_admin_msg, admin_msg)
        self.assertEqual(cmd_list, [])
  
    def test_text_from_new_sender_gets_to_new_sender_mms(self):
        response = self.User1.make_text_only_request(body='help')
        self.assertIn('New sender: Request first image & link to specific instructions', str(response.content))



class ViewTwi_Recorder_NewSendersCases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = CarepostUser(name='user1')

    def test_twi_recorder_announcement__before_media_received_gives_audio_instruction_and_sms_link(self):
        response = self.User1.make_twi_voice_recorder_start_request()
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('</Say><Record maxLength="120"/>', str(response.content))
        self.assertIn('To use this, please text the system an image first', str(response.content))
        self.assertIn('New sender unexpected call to twilio', admin_list[0])

    def test_twi_recorder_message__before_media_received_gives_instruction_link(self):
        response = self.User1.make_twi_recordering_done_request()
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('New sender instructions link on unexpected call to twilio', str(response.content))
        self.assertEqual([], admin_list)

    def test_twi_recorder_instructs_on_audio_recording_if_image_already_received(self):
        self.User1.make_media_request(media=IMAGE)
        filerviews.clear_the_sqs_queue_TEST_SQS()
        response = self.User1.make_twi_voice_recorder_start_request()
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('welcome to the postcard system audio function. The system got your photo', str(response.content))
        self.assertEqual(admin_list, [])

    def test_twi_recorder_gives__congrats_if_image_already_received(self):
        self.User1.make_media_request(media=IMAGE)
        filerviews.clear_the_sqs_queue_TEST_SQS()
        response = self.User1.make_twi_recordering_done_request()
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('Congrats to new sender', str(response.content))
        self.assertEqual(admin_list, [])



class View_Whole_Process__NewSendersCases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = CarepostUser(name='user1')

    def test_all_through_profile_error(self):
        self.User1.make_media_request(media=IMAGE)
        self.User1.make_twi_recordering_done_request()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        response = self.User1.make_media_request(media=IMAGE, body='Xprofile')
        admin_list, cmd_list = get_all_sqs()
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        self.assertIn('New sender profile instruction & link to specific instructions', str(response.content))
        self.assertEqual(cmd_list, [])
        self.assertIn('error: expect profile', admin_list[0])
        self.assertEqual(expect, 'profile')
 
    def test_all_through_good_profile(self):
        self.User1.make_media_request(media=IMAGE)
        self.User1.make_twi_recordering_done_request()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        response = self.User1.make_media_request(media=IMAGE, body='profile')
        admin_list, cmd_list = get_all_sqs()
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        self.assertIn('New sender complete welcome message', str(response.content))
        self.assertEqual(len(cmd_list), 1)
        new_cmd = cmd_list[0]
        self.assertEqual(new_cmd['event'], 'new_postcard')
        self.assertEqual(new_cmd['context'], 'NewSenderFirst')
        self.assertIn('sent_at', new_cmd)
        self.assertIn('profile_url', new_cmd)
        self.assertEqual(admin_list, [])
        self.assertEqual(expect, 'new_sender_ready')

    def test_postcard_made_through_free_tier_calls_when_new_sender_expect_is___new_sender_ready(self):
        self.User1.make_media_request(media=IMAGE)
        self.User1.make_twi_recordering_done_request()
        self.User1.make_media_request(media=IMAGE, body='profile')
        self.User1.make_media_request(media=IMAGE)
        filerviews.clear_the_sqs_queue_TEST_SQS()
        response = self.User1.make_twi_recordering_done_request()
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('free_tier postcard sent', str(response.content))
        self.assertEqual(len(cmd_list), 1)
        self.assertEqual(admin_list, [])
        self.assertEqual(expect, 'new_sender_ready')
        new_cmd = cmd_list[0]
        self.assertEqual(new_cmd['event'], 'new_postcard')
        