from django.test import TestCase
from .exceptions import S3KeyNotFound

from . import views 

class ViewAcceptMediaGoodPushCaseTest(TestCase):
    def setUp(self) -> None:
        views.clear_the_read_bucket()

    def test_missing_key_raises_exception_in____load_a_thing_using_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views._load_a_thing_using_key('+newphonenumber')

    def test_load_twitalk_freetier_raises_exception_on_missing_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views.load_twitalk_freetier('+newphonenumber')
       
    def test_load_new_sender_raises_exception_on_missing_key(self):
        with self.assertRaises(S3KeyNotFound):
            res = views.load_new_sender('+newphonenumber')
       
    def test_can_save_new_sender_and_read_it(self):
        views.save_new_sender_state('+newphonenumber', {'greet': 'hi there'})
        res = views.load_new_sender('+newphonenumber')
        self.assertEqual(res['greet'], 'hi there')
        print(res)
       


