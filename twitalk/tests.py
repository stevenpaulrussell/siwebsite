import time

from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponse


from filer import views as filerviews 
from .new_sender import mms_from_new_sender, recorder_from_new_sender
from .free_tier import mms_to_free_tier, recorder_to_free_tier

AUDIO = 'audio/ogg'
IMAGE = 'image/jpeg'

class SiWebCarepostUser:         
    to_0 = '+1twilio_test_phone_0'
    to_1 = '+1twilio_test_phone_1'
    url0 = 'media_url_0'
    url1 = 'media_url_1'
    url2 = 'media_url_2'

    def __init__(self, name, mobile_number=None) -> None:
        self.user_name = name
        self.user_mobile_number = mobile_number or f'{name}_+1mobile_number'

    def set_blank_mms_key_values_from_view(self, **kwds):
        key_values = dict(timestamp=time.time(), from_tel=self.user_mobile_number, 
                                to_tel=SiWebCarepostUser.to_0, text='', image_url=None)
        key_values.update(kwds)
        return key_values

    def set_blank_recorder_key_values_from_view(self, **kwds):
        postdata={}
        key_values = dict(timestamp=time.time(), from_tel=self.user_mobile_number, 
                                to_tel=SiWebCarepostUser.to_0, postdata=postdata)
        key_values.update(kwds)
        return key_values

    def set_RecordingUrl_recorder_key_values_from_view(self, **kwds):
        postdata=dict(RecordingUrl=SiWebCarepostUser.url0)
        key_values = dict(timestamp=time.time(), from_tel=self.user_mobile_number, 
                                to_tel=SiWebCarepostUser.to_0, postdata=postdata)
        key_values.update(kwds)
        return key_values


def get_all_sqs():
    # In Test, both admin and cmd sqs go to test_sqs.
    # This function reads the one sqs queue, and demuxes
    # messages based on structure
    admin_list = []
    cmd_list = []
    while True:
        msg = filerviews.get_an_sqs_message()
        if isinstance(msg, str):
            admin_list.append(msg)
        elif isinstance(msg, dict):
            cmd_list.append(msg)
        else:
            break
    return admin_list, cmd_list


class New_Sender_Common_Test_Cases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')

    def test_text_only(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(text='some random text')
        from_tel_msg = mms_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(cmd_list), 0)
        self.assertEqual(expect, 'image')
        self.assertIn('New sender <user1_+1mobile_number>, missing plain image', admin_list[0])
        self.assertIn('New sender: Request first image & link to specific instructions', from_tel_msg)

    def test_image_only(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        from_tel_msg = mms_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(cmd_list), 0)
        self.assertEqual(expect, 'audio')
        self.assertIn('New sender <user1_+1mobile_number>, image OK', admin_list[0])
        self.assertIn('New sender welcome: image recvd', from_tel_msg)

    def test_call_to_make_audio_when_image_present(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**key_values)
        get_all_sqs()    # Dump this first set
        key_values = self.User1.set_blank_recorder_key_values_from_view() 
        from_tel_msg = recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('Hello, and welcome to the postcard system audio function.', from_tel_msg)
        self.assertEqual(admin_list, [])
        self.assertEqual(cmd_list, [])
        self.assertEqual(expect, 'audio')

    def test_call_to_make_audio_when_image_NOT_present(self):
        # New sender calls the number but has not sent an image
        key_values = self.User1.set_blank_recorder_key_values_from_view() 
        from_tel_msg =  recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(admin_list, ['New sender unexpected call to twilio.'])
        self.assertEqual(cmd_list, [])
        self.assertIn('To use this, please text the system an image first.', from_tel_msg)
        self.assertEqual(expect, 'image')

    def test_audio_delivery_when_image_present(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**key_values)
        get_all_sqs()    # Dump this first set
        key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        from_tel_msg =  recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(from_tel_msg, 'Congrats to new sender making a first postcard.')
        self.assertEqual(admin_list, [])
        self.assertEqual(cmd_list, [])
        self.assertEqual(expect, 'profile')

    def test_audio_delivery_when_image_NOT_present(self):
        # The recording is being delivered
        key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        from_tel_msg =  recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(admin_list, [])
        self.assertEqual(cmd_list, [])
        self.assertEqual(from_tel_msg, 'New sender instructions link on unexpected call to twilio.')
        self.assertEqual(expect, 'image')

    def test_profile_delivered_finish_enrollment(self):
        image_key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**image_key_values)
        audio_key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        recorder_from_new_sender(**audio_key_values)
        get_all_sqs()    # Dump this first set
        profile_key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0, text='profile')
        from_tel_msg = mms_from_new_sender(**profile_key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(from_tel_msg, 'New sender complete welcome message')
        self.assertEqual(admin_list, [])
        self.assertEqual(len(cmd_list), 1)
        command = cmd_list[0]
        self.assertEqual(command['cmd'], 'first_postcard')
        self.assertEqual(expect, 'new_sender_ready')



class Free_Tier_Common_Test_Cases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')
        filerviews.update_free_tier(self.User1.user_mobile_number, SiWebCarepostUser.to_0)

    def test_text_for_help(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(text='help')
        from_tel_msg = mms_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(len(admin_list), 0)
        self.assertEqual(len(cmd_list), 0)
        self.assertIn('Free tier help: Link to instructions', from_tel_msg)

    def test_text_profile_with_image(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0, text='profile')
        from_tel_msg = mms_to_free_tier(**key_values, free_tier_morsel={})
        # text='profile'   # 'help' or 'profile' get specific action. All else sent as cmd 'cmd general'
        # key_values = self.User1.set_blank_mms_key_values_from_view(text=text)
        # from_tel_msg = mms_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(len(admin_list), 0)
        self.assertEqual(len(cmd_list), 1)
        cmd_from_list = cmd_list[0]
        self.assertEqual(cmd_from_list['cmd'], 'profile')
        self.assertIn('Your profile will be updated shortly, and you will be notified', from_tel_msg)

    def test_text_random_only(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(text='some random text')
        from_tel_msg = mms_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(len(admin_list), 0)
        self.assertEqual(len(cmd_list), 1)
        cmd_from_list = cmd_list[0]
        self.assertEqual(cmd_from_list['cmd'], 'cmd_general')
        self.assertIn('Your command <some random text> is queued for processing... you will hear back!', from_tel_msg)

    def test_image_only(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        from_tel_msg = mms_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(len(admin_list), 0)
        self.assertEqual(len(cmd_list), 0)
        self.assertIn('Good image received free tier', from_tel_msg)

    def test_call_to_make_audio_when_image_present(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_to_free_tier(**key_values, free_tier_morsel={})
        get_all_sqs()    # Dump this first set
        key_values = self.User1.set_blank_recorder_key_values_from_view() 
        from_tel_msg = recorder_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertIn('free_tier recording announcement OK image', from_tel_msg)
        self.assertEqual(admin_list, [])
        self.assertEqual(cmd_list, [])

    def test_call_to_make_audio_when_image_NOT_present(self):
        # Free tier sender calls the number but has not sent an image
        key_values = self.User1.set_blank_recorder_key_values_from_view(free_tier_morsel={}) 
        from_tel_msg =  recorder_to_free_tier(**key_values)
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(admin_list, [])
        self.assertEqual(cmd_list, [])
        self.assertIn('free_tier recording announcement without image', from_tel_msg)

    def test_audio_delivery_when_image_present(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_to_free_tier(**key_values, free_tier_morsel={})
        get_all_sqs()    # Dump this first set
        key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        from_tel_msg =  recorder_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(from_tel_msg, 'free_tier postcard sent')
        self.assertEqual(admin_list, [])
        self.assertEqual(len(cmd_list), 1)
        cmd_from_list = cmd_list[0]
        self.assertEqual(cmd_from_list['cmd'], 'new_postcard')

    def test_audio_delivery_when_image_NOT_present(self):
        # The recording is being delivered
        key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        from_tel_msg =  recorder_to_free_tier(**key_values, free_tier_morsel={})
        admin_list, cmd_list = get_all_sqs()
        self.assertEqual(admin_list, [])
        self.assertEqual(cmd_list, [])
        self.assertEqual(from_tel_msg, 'free tier ask to call & make recording & link to instructions.')
