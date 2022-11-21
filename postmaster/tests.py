from django.test import TestCase

# Create your tests here.
from filer import views as filerviews 
from twitalk.tests import SiWebCarepostUser


class Postcard_commands(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()
        self.User1 = SiWebCarepostUser(name='user1')
        filerviews.update_free_tier(self.User1.user_mobile_number, SiWebCarepostUser.to_0)

    def test_test_setup(self):
        self.assertTrue('Got one none-test to work')
