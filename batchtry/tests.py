
# import os
# import json
# import time
# import pprint
# import webbrowser

# from django.test import TestCase

# import postoffice 
# from filer import views as filerviews 
# from saveget import saveget
# import twitalk
# from . import views as old_filer

# pp = pprint.PrettyPrinter(indent=2)

# data_source = os.environ['POSTBOX_DATA_SOURCE']

# from_Steve = '+16502196500'
# from_Nancy = '+16502185923'
# from_Ryan = '+16508159597'
# from_Zach = '+12068173605'
# from_Josh = '+16508151092'
# from_David = '+12134475412'
# wanted_tel_ids = [from_Steve, from_Nancy, from_Ryan, from_Zach, from_Josh]

# # Keep Josh who has not been sending??
# wanted_tel_ids.remove(from_Josh)

# # Get all the old stuff, arrange for use in the transfer
# old_filer.aws_read_bucket_name = 'real-software-bucket'
# all_state = old_filer.load_state_from_s3()
# senders, po, c_in_p, conns, po_admin = all_state
# some_cards = old_filer.get_cards(limit=15)

# # f: tel_id, t: svc_id.  Gerry's pobox_id in the old system was '27f12208-......'
# gerry_links = {f: t for f in conns for t in conns[f] if '27f12208-' in conns[f][t]['po_box_uuid']}
# # Keep Josh, David who have not been sending??
# gerry_links.pop(from_Josh)
# gerry_links.pop(from_David)

# pobox = {}
# for card in some_cards:
#     f, t = card['addressing']['tel_id'], card['addressing']['svc_id']
#     if f in gerry_links and  t == gerry_links[f]:
#         try:
#             pobox[f].append(card)
#         except KeyError:
#             pobox[f] = [card]

# def when(card):
#     return card['addressing']['sent_at']
    
# for cardlist in pobox.values():
#     cardlist.sort(key=when)
#     if len(cardlist) > 2:
#         cardlist = cardlist[:2]


# def nq_one_sender(tel_id, svc_id):
#     sender = senders[tel_id]
#     svc_id = gerry_links[tel_id]
#     profile_url = sender['profile_photo_url']
#     first_card = pobox[tel_id].pop(0)
#     image_url = first_card['image']['media_url']
#     image_when = first_card['image']['post_time']
#     audio_url = first_card['audio']['media_url']
#     audio_when = first_card['audio']['post_time']
#     wip = dict(image_timestamp=image_when, image_url=image_url, audio_timestamp=audio_when, audio_url=audio_url)  
#     filerviews.nq_postcard(tel_id, svc_id, wip=wip, profile_url=profile_url, context='NewSenderFirst')     

# def dq_events_and_do_one_event(count):
#     events = []
#     messages = []
#     for i in range(count):
#         event = saveget.get_one_sqs_event()
#         if not event:
#             break
#         events.append(event)
#         message = postoffice.event_handler.interpret_one_event(event)
#         messages.append(message)
#     return events

# def dq_admin(count):
#     msgs = []
#     for i in range(count):
#         msg = saveget.get_one_sqs_admin()
#         if msg:
#             msgs.append(msg)
#     return msgs

# def sim_get_a_passkey(tel_id, svc_id):
#     """Use twitalk to get a passkey returned.  Have postbox read the sqs cmd and store that passkey"""
#     passkey_msg = sim_cmd(tel_id, svc_id, cmd='passkey')    
#     passkey = passkey_msg.split('"')[1]
#     return passkey

# def sim_cmd(tel_id, svc_id, cmd, image_url=None):
#     now = time.time()
#     # The following line generates a command in sqs....
#     cmd_msg = twitalk.free_tier.mms_to_free_tier(now, tel_id, svc_id, cmd, image_url, free_tier_morsel=None)    
#     return cmd_msg

# def send_a_postcard_to_pobox(tel_id, svc_id):
#     card = pobox[tel_id].pop(0)
#     image_url = card['image']['media_url']
#     image_when = card['image']['post_time']
#     audio_url = card['audio']['media_url']
#     audio_when = card['audio']['post_time']
#     wip = dict(image_timestamp=image_when, image_url=image_url, audio_timestamp=audio_when, audio_url=audio_url)  
#     filerviews.nq_postcard(tel_id, svc_id, wip=wip, context='HaveViewer')     




# class OneCmdTests(TestCase):
#     def setUp(self) -> None:
#         filerviews.clear_the_read_bucket()
#         filerviews.clear_the_sqs_queue_TEST_SQS()

#     def test_build_one_step_at_a_time(self):
#         for tel_id in gerry_links:
#             nq_one_sender(tel_id, svc_id=gerry_links[tel_id])
#         cmd_msgs = dq_events_and_do_one_event(count=10)
#         admin_msgs = dq_admin(count=10)
#         twitalk_sender  =  filerviews.load_from_free_tier(from_Steve)  # twitalk cannot see much state
#         postoffice_sender = saveget.get_sender(from_Steve)             # Whole state available to postoffice
#         svc_id_used_by_Steve = gerry_links[from_Steve]
#         self.assertIn(svc_id_used_by_Steve, twitalk_sender)
#         self.assertEqual(twitalk_sender[svc_id_used_by_Steve]['sender_moniker'], '6 5 0 0')
#         self.assertIn('profile_url', postoffice_sender)
#         self.assertEqual(len(cmd_msgs), 4)
#         self.assertEqual(len(admin_msgs), 4)
#         self.assertIn('using new svc_id', admin_msgs[0])
#         # Connect a viewer and get a new pobox_id: connect_viewer guarded by a form checking a passkey, not tested here.
#         pobox_id = postoffice.views.new_pobox_id(postoffice_sender, svc_id_used_by_Steve) 
#         pobox_url = f'{data_source}/player/postbox/{pobox_id}'
#         # Steve connect the other senders to the viewer. Other senders each start by getting a passkey
#         for tel_id in [from_Nancy, from_Ryan, from_Zach]:
#             passkey = sim_get_a_passkey(tel_id, svc_id=gerry_links[tel_id])
#             dq_events_and_do_one_event(count=2)      # . postoffice finds the passkey and stores it
#             admin_msgs = dq_admin(count=10)
#             connect_cmd = f'connect {tel_id} passkey {passkey}'
#             returned_msg = sim_cmd(from_Steve, svc_id_used_by_Steve, connect_cmd)    
#             self.assertIn(f'connect {tel_id} passkey', returned_msg)
#             self.assertIn('is queued for processing... you will hear back!', returned_msg)
#             dq_events_and_do_one_event(count=2)
#         # Send postcards, these will  be the first to be put into that newly set pobox!
#         for tel_id in [from_Steve, from_Nancy, from_Ryan, from_Zach]:
#             svc_id = gerry_links[tel_id]
#             send_a_postcard_to_pobox(tel_id, svc_id=gerry_links[tel_id])
#             dq_events_and_do_one_event(count=2)
#         # See that it works!  And it does!
#         # webbrowser.open(pobox_url)



