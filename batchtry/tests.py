
import os
import json
import time
import pprint
import webbrowser

from django.test import TestCase

import postoffice 
from filer import views as filerviews 
from saveget import saveget
import twitalk
from . import views as old_filer

pp = pprint.PrettyPrinter(indent=2)

data_source = os.environ['POSTBOX_DATA_SOURCE']
from_Steve = '+16502196500'
from_Nancy = '+16502185923'
from_Ryan = '+16508159597'
from_Zach = '+12068173605'
from_Josh = '+16508151092'
wanted_from_tels = [from_Steve, from_Nancy, from_Ryan, from_Zach, from_Josh]

# Keep Josh who has not been sending??
wanted_from_tels.remove(from_Josh)

# Get all the old stuff, arrange for use in the transfer
old_filer.aws_read_bucket_name = 'real-software-bucket'
all_state = old_filer.load_state_from_s3()
senders, po, c_in_p, conns, po_admin = all_state
some_cards = old_filer.get_cards(limit=15)

# f: from_tel, t: to_tel.  Gerry's pobox_id in the old system was '27f12208-......'
gerry_links = {f: t for f in conns for t in conns[f] if '27f12208-' in conns[f][t]['po_box_uuid']}
# Keep Josh who has not been sending??
gerry_links.pop(from_Josh)

pobox = {}
for card in some_cards:
    f, t = card['addressing']['from_tel'], card['addressing']['to_tel']
    if f in gerry_links and  t == gerry_links[f]:
        try:
            pobox[f].append(card)
        except KeyError:
            pobox[f] = [card]

def when(card):
    return card['addressing']['sent_at']
    
for cardlist in pobox.values():
    cardlist.sort(key=when)
    if len(cardlist) > 2:
        cardlist = cardlist[:2]


def nq_one_sender(from_tel):
    sender = senders[from_tel]
    to_tel = gerry_links[from_tel]
    profile_url = sender['profile_photo_url']
    first_card = pobox[from_tel][0]
    image_url = first_card['image']['media_url']
    image_when = first_card['image']['post_time']
    audio_url = first_card['audio']['media_url']
    audio_when = first_card['audio']['post_time']
    wip = dict(image_timestamp=image_when, image_url=image_url, audio_timestamp=audio_when, audio_url=audio_url)  
    filerviews.nq_postcard(from_tel, to_tel, wip=wip, profile_url=profile_url, context='NewSenderFirst')     

def dq_cmds_and_admin(count):
    msgs = []
    for i in range(count):
        msg = postoffice.cmds.dq_and_do_one_cmd()
        if msg:
            msgs.append(msg)
    return msgs

def sim_get_a_passkey(from_tel, to_tel):
    """Use twitalk to get a passkey returned.  Have postbox read the sqs cmd and store that passkey"""
    passkey_msg = sim_cmd(from_tel, to_tel, cmd='passkey')    
    passkey = passkey_msg.split('"')[1]
    return passkey

def sim_cmd(from_tel, to_tel, cmd, image_url=None):
    now = time.time()
    # The following line generates a command in sqs....
    cmd_msg = twitalk.free_tier.mms_to_free_tier(now, from_tel, to_tel, cmd, image_url, free_tier_morsel=None)    
    return cmd_msg




class OneCmdTests(TestCase):
    def setUp(self) -> None:
        filerviews.clear_the_read_bucket()
        filerviews.clear_the_sqs_queue_TEST_SQS()

    def test_build_one_step_at_a_time(self):
        for from_tel in gerry_links:
            nq_one_sender(from_tel)
        msgs = dq_cmds_and_admin(count=10)
        twitalk_sender  =  filerviews.load_from_free_tier(from_Steve)  # twitalk cannot see much state
        postoffice_sender = saveget.get_sender(from_Steve)             # Whole state available to postoffice
        to_tel_used_by_Steve = gerry_links[from_Steve]
        self.assertIn(to_tel_used_by_Steve, twitalk_sender)
        self.assertEqual(twitalk_sender[to_tel_used_by_Steve]['from'], '6 5 0 0')
        self.assertIn('profile_url', postoffice_sender)
        self.assertEqual(len(msgs), 4)
        self.assertIn('using new to_tel', msgs[0])
        # Connect a viewer and get a new pobox_id: connect_viewer guarded by a form checking a passkey, not tested here.
        pobox_id = postoffice.connects.connect_viewer(postoffice_sender, to_tel_used_by_Steve) 
        pobox_url = f'{data_source}/postbox/{pobox_id}'
        # View the pobox, which if seen now only has Steve as a sender
        # webbrowser.open(pobox_url)
        # Now connect the other senders to the viewer, start by getting a passkey
        for from_tel in [from_Nancy, from_Ryan, from_Zach]:
            to_tel = gerry_links[from_tel]
            passkey = sim_get_a_passkey(from_tel, to_tel)
            passkey_msgs = dq_cmds_and_admin(count=3)
            connect_cmd = f'connect {from_tel} passkey {passkey}'
            connect_msg = sim_cmd(from_Steve, to_tel_used_by_Steve, connect_cmd)    
            admin_msgs = dq_cmds_and_admin(count=3)
            print(f'{from_tel}  passkey_msgs {passkey_msgs}')
            print(f'{from_tel} connect_msg {connect_msg}')
            print(f'{from_tel} admin_msgs {admin_msgs}')
        webbrowser.open(pobox_url)
        


        




    """
    nq_new_senders: postcard and profile

    dq_cmds

    (check result)

    viewer 2196500

    connect ~ 2196500

    send 2 postcards
    
    """


#  pp.pprint(a_card)

# Get postcards ordered by time.
# Get senders ordered by from_tel
# Get connections ordered by from_tel

# 1. From a list of wanted senders, for each sender, get oldest card and profile and nq the sender.
# 2. Connect the 650.219... to the established pobox_id, adding a key value to do this into connects.connect_viewer
# 3. For each of the others, run connect command by getting passkey in twitalk (doing nq write and read) and...
#       running connect command, sent from free_tier.
#  ==> write this as a functional test, which it is, but produces a useful result. After each step, test and
#       maybe print for inspection.
#       Write all this in test_  !!
#


