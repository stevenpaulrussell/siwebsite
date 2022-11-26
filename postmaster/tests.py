from django.test import TestCase

# Create your tests here.
from filer import views as filerviews 
from twitalk.tests import SiWebCarepostUser
from . import postcards


class Postcard_commands(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')
        filerviews.update_free_tier(self.User1.user_mobile_number, SiWebCarepostUser.to_0)

    def test_create_new_sender(self):
        sender = postcards.create_new_sender('from_tel', 'profile_url')
        self.assertEqual(sender['version'], 1)

    def test_create_new_connection(self):
        sender = postcards.create_new_sender('from_tel', 'profile_url')
        pre_conn = sender['conn'].copy()
        postcards.create_new_connection(sender, 'from_tel')
        post_conn = sender['conn']['from_tel']
        self.assertEqual(pre_conn, {})
        self.assertEqual(post_conn['to'], 'kith or kin')
        print(f'line 27 postmaster.postcards post_conn: <{post_conn}>')
