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


class New_Sender_Test_Cases(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')

    def test_text_only_from_new_sender(self):
        key_values = self.User1._set_key_values_from_view(text='some random text')
        mms_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(sms_list), 1)
        self.assertEqual(expect, 'image')
        self.assertIn('New sender <user1_+1mobile_number>, missing plain image', admin_list[0])
        self.assertIn('New sender: Request first image. Also, link to instructions as second msg?', sms_list[0].values())

    def test_image_only_from_new_sender(self):
        key_values = self.User1._set_key_values_from_view(image_url=SiWebCarepostUser.url0)
        mms_from_new_sender(**key_values)
        expect = filerviews.load_from_new_sender(self.User1.user_mobile_number)
        admin_list, sms_list = get_all_sqs()
        self.assertEqual(len(admin_list), 1)
        self.assertEqual(len(sms_list), 1)
        self.assertEqual(expect, 'audio')
        self.assertIn('New sender <user1_+1mobile_number>, image OK', admin_list[0])
        self.assertIn('New sender sends image', sms_list[0].values())


