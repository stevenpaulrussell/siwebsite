import time
import uuid
import pprint


# from django.test import TestCase

# from filer import views as filerviews 
# from saveget import saveget
# from postoffice import cmds, connects
# from postbox.views import update_viewer_data


class TwiSim:
    def __init__(self, name):
        self.mobile = f'mobile_{name}'
        self.twi_directory = dict(twil0=f'twil0_{name}', twil1=f'twil1_{name}')
        self.profile_url = f'profile_{name}'
        self.url_count = 0

    def _cmd_common(self, twinumber, **message):
        message['event'] = 'cmd_general'
        message['sent_at'] = time.time()
        message['from_tel'] = self.mobile
        message['to_tel'] = self.twi_directory[twinumber]
        return message

    def _make_wip(self):
        wip = dict(image_timestamp='image_timestamp', audio_timestamp='audio_timestamp')
        wip['image_url'] = f'image_url{self.url_count}'
        wip['audio_url'] = f'audio_url{self.url_count}'
        ++self.url_count
        return wip

    def _new_postcard_common(self, twinumber):
        postcard_common = self._cmd_common(twinumber)
        postcard_common['event'] = 'new_postcard'
        postcard_common['wip'] = self._make_wip()
        return postcard_common

    def newsender_firstpostcard(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NewSenderFirst'
        sqs_message['profile_url'] = self.profile_url
        return sqs_message

    def newrecipient_postcard(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NewRecipientFirst'
        return sqs_message

    def newpostcard_noviewer(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'NoViewer'
        return sqs_message

    def newpostcard_haveviewer(self, twinumber='twil0'):
        sqs_message = self._new_postcard_common(twinumber)
        sqs_message['context'] = 'HaveViewer'
        return sqs_message

    
    def set_profile(self, twinumber, profile_url):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['event'] = 'profile'
        sqs_message['profile_url'] = profile_url
        return sqs_message

    def set_from(self, twinumber, some_name):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['text'] = f'from: {some_name}'
        return sqs_message

    def set_to(self, twinumber, some_name):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['text'] = f'to: {some_name}'
        return sqs_message

    def passkey(self, twinumber):
        sqs_message = self._cmd_common(twinumber)
        sqs_message['event'] = 'passkey'
        sqs_message['passkey'] = str(uuid.uuid4())[0:4]
        sqs_message['expire'] = time.time() + 24*60*60
        return sqs_message

    def connect(self, twilnumber, requestor_from_tel, passkey):
        sqs_message = self._cmd_common(twilnumber)
        sqs_message['text'] = f'connect {requestor_from_tel} passkey {passkey}'
        return sqs_message

pp = pprint.PrettyPrinter(indent=2)
