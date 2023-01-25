import requests
import json
import os

from django.test import TestCase

from . import views

data_source = os.environ['POSTBOX_DATA_SOURCE']


class TestPostmasterFunctions(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_tickles_via_call(self):
        Http_Resp_cmds_and_admins = views.tickles('request stand-in')
        cmds_and_admins = json.loads(Http_Resp_cmds_and_admins.content)
        self.assertIn('admin_msgs', cmds_and_admins)

    def test_tickles_via_url(self):
        tickles_url = f'{data_source}/tickles'
        Http_Resp_cmds_and_admins = requests.get(tickles_url)
        cmds_and_admins = json.loads(Http_Resp_cmds_and_admins.content)
        self.assertIn('admin_msgs', cmds_and_admins)

