import time

from django.test import TestCase
from django.test.client import RequestFactory
from django.http import HttpResponse


from filer import views as filerviews 
from .new_sender import mms_from_new_sender, recorder_from_new_sender

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
    admin_list = []
    sms_list = []
    while True:
        msg = filerviews.get_an_sqs_message()
        if isinstance(msg, str):
            admin_list.append(msg)
        elif isinstance(msg, dict):
            sms_list.append(msg)
        else:
            break
    return admin_list, sms_list


class New_Sender_Common_Test_Cases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')

    def test_text_only(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(text='some random text')
        from_tel_msg = mms_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(sms_list), 0)
        self.assertEqual(expect, 'image')
        self.assertIn('New sender <user1_+1mobile_number>, missing plain image', admin_list[0])
        self.assertIn('New sender: Request first image. Also, link to instructions as second msg?', from_tel_msg)

    def test_image_only(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        from_tel_msg = mms_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(sms_list), 0)
        self.assertEqual(expect, 'audio')
        self.assertIn('New sender <user1_+1mobile_number>, image OK', admin_list[0])
        self.assertIn('New sender welcome image', from_tel_msg)

    def test_call_to_make_audio_when_image_present(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**key_values)
        get_all_sqs()    # Dump this first set
        key_values = self.User1.set_blank_recorder_key_values_from_view() 
        from_tel_msg = recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertIn('Hello, and welcome to the postcard system audio function.', from_tel_msg)
        self.assertEqual(admin_list, [])
        self.assertEqual(sms_list, [])
        self.assertEqual(expect, 'audio')

    def test_call_to_make_audio_when_image_NOT_present(self):
        # New sender calls the number but has not sent an image
        key_values = self.User1.set_blank_recorder_key_values_from_view() 
        from_tel_msg =  recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(admin_list, [])
        self.assertEqual(sms_list, [])
        self.assertIn('To use this, please text the system an image first.', from_tel_msg)
        self.assertEqual(expect, 'image')

    def test_audio_delivery_when_image_present(self):
        key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**key_values)
        get_all_sqs()    # Dump this first set
        key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        from_tel_msg =  recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(from_tel_msg, 'Congrats to new sender making a first postcard.')
        self.assertEqual(admin_list, [])
        self.assertEqual(sms_list, [])
        self.assertEqual(expect, 'profile')

    def test_audio_delivery_when_image_NOT_present(self):
        # The recording is being delivered
        key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
        from_tel_msg =  recorder_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(admin_list, [])
        self.assertEqual(sms_list, [])
        self.assertEqual(from_tel_msg, 'Send instruction link to instructions.')
        self.assertEqual(expect, 'image')


class Free_Tier_Common_Test_Cases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')
        # Set up a free_tier sender in filer.
            # f'free_tier/{from_tel}':                # These are written by postmaster, read by twitalk.
            #         f'{to_tel}':  
            #         'from': -> sender name if key 'from' is present        # Use to customize sms to sender
            #         'to': -> recipient name if key is present         # Use to customize sms to sender

    def test_text_only(self):
        self.assertFalse('No more work to do in free_tier testing, but it should be easy!!')
        # key_values = self.User1.set_blank_mms_key_values_from_view(text='some random text')
        # from_tel_msg = mms_from_new_sender(**key_values)
        # expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        # admin_list, sms_list = get_all_sqs()
        # self.assertEqual(len(admin_list), 1)
        # self.assertEqual(len(sms_list), 0)
        # self.assertEqual(expect, 'image')
        # self.assertIn('New sender <user1_+1mobile_number>, missing plain image', admin_list[0])
        # self.assertIn('New sender: Request first image. Also, link to instructions as second msg?', from_tel_msg)

    # def test_image_only(self):
    #     key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
    #     from_tel_msg = mms_from_new_sender(**key_values)
    #     expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
    #     admin_list, sms_list = get_all_sqs()
    #     self.assertEqual(len(admin_list), 1)
    #     self.assertEqual(len(sms_list), 0)
    #     self.assertEqual(expect, 'audio')
    #     self.assertIn('New sender <user1_+1mobile_number>, image OK', admin_list[0])
    #     self.assertIn('New sender welcome image', from_tel_msg)

    # def test_call_to_make_audio_when_image_present(self):
    #     key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
    #     mms_from_new_sender(**key_values)
    #     get_all_sqs()    # Dump this first set
    #     key_values = self.User1.set_blank_recorder_key_values_from_view() 
    #     from_tel_msg = recorder_from_new_sender(**key_values)
    #     expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
    #     admin_list, sms_list = get_all_sqs()
    #     self.assertIn('Hello, and welcome to the postcard system audio function.', from_tel_msg)
    #     self.assertEqual(admin_list, [])
    #     self.assertEqual(sms_list, [])
    #     self.assertEqual(expect, 'audio')

    # def test_call_to_make_audio_when_image_NOT_present(self):
    #     # New sender calls the number but has not sent an image
    #     key_values = self.User1.set_blank_recorder_key_values_from_view() 
    #     from_tel_msg =  recorder_from_new_sender(**key_values)
    #     expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
    #     admin_list, sms_list = get_all_sqs()
    #     self.assertEqual(admin_list, [])
    #     self.assertEqual(sms_list, [])
    #     self.assertIn('To use this, please text the system an image first.', from_tel_msg)
    #     self.assertEqual(expect, 'image')

    # def test_audio_delivery_when_image_present(self):
    #     key_values = self.User1.set_blank_mms_key_values_from_view(image_url=SiWebCarepostUser.url0)
    #     mms_from_new_sender(**key_values)
    #     get_all_sqs()    # Dump this first set
    #     key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
    #     from_tel_msg =  recorder_from_new_sender(**key_values)
    #     expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
    #     admin_list, sms_list = get_all_sqs()
    #     self.assertEqual(from_tel_msg, 'Congrats to new sender making a first postcard.')
    #     self.assertEqual(admin_list, [])
    #     self.assertEqual(sms_list, [])
    #     self.assertEqual(expect, 'profile')

    # def test_audio_delivery_when_image_NOT_present(self):
    #     # The recording is being delivered
    #     key_values = self.User1.set_RecordingUrl_recorder_key_values_from_view() 
    #     from_tel_msg =  recorder_from_new_sender(**key_values)
    #     expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
    #     admin_list, sms_list = get_all_sqs()
    #     self.assertEqual(admin_list, [])
    #     self.assertEqual(sms_list, [])
    #     self.assertEqual(from_tel_msg, 'Send instruction link to instructions.')
    #     self.assertEqual(expect, 'image')
