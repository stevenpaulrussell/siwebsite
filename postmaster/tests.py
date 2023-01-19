import requests
import json

from django.test import TestCase

from . import views

class TestPostmasterFunctions(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_tickles_via_call(self):
        Http_Resp_cmds_and_admins = views.tickles('request stand-in')
        cmds_and_admins = json.loads(Http_Resp_cmds_and_admins.content)
        self.assertIn('admin_msgs', cmds_and_admins)


