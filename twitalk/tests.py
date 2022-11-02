import time

from django.test import TestCase
from django.test.client import RequestFactory

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

    def _set_key_values_from_view(self, **kwds):
        key_values = dict(timestamp=time.time(), from_tel=self.user_mobile_number, 
                                to_tel=SiWebCarepostUser.to_0, text='', image_url=None)
        key_values.update(kwds)
        return key_values


class New_Sender_Test_Cases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')

    def test_text_only_from_new_sender(self):
        key_values = self.User1._set_key_values_from_view(text='some random text')
        mms_from_new_sender(**key_values)
        res = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        msg1 = filerviews.get_an_sqs_message()
        msg2 = filerviews.get_an_sqs_message()
        msg3 = filerviews.get_an_sqs_message()
        self.assertIsNone(msg3)
        self.assertEqual(res, 'image')
        print(f'\n msg1:\n{msg1}\n')
        print(f'\n msg2:\n{msg2}\n')

    def test_image_only_from_new_sender(self):
        key_values = self.User1._set_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**key_values)
        res = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        msg1 = filerviews.get_an_sqs_message()
        msg2 = filerviews.get_an_sqs_message()
        msg3 = filerviews.get_an_sqs_message()
        self.assertIsNone(msg3)
        self.assertEqual(res, 'audio')
        print(f'\n msg1:\n{msg1}\n')
        print(f'\n msg2:\n{msg2}\n')


