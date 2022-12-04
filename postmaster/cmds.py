import os
import json
import time

import saveget, postcards, connects


def interpret_one_cmd(cmd_json):
    cmd_dict = json.loads(cmd_json)
    cmd = cmd_dict['cmd']
    from_tel = cmd_dict('from_tel')
    to_tel = cmd_dict('to_tel')
    sender = saveget.get_sender(from_tel)
    sender['heard_from'] = time.time()
    match cmd:
        case 'new_postcard':
            message = postcards.new_postcard(from_tel, to_tel, **msg)
        case 'profile':
            sender['profile_url'] = cmd_dict['profile_url']
            message = f'OK, your profile image has been updated.'
        case 'cmd_general':
            message = handle_possible_cmd_general(from_tel, to_tel, sender, cmd_dict['text'])

def handle_possible_cmd_general(from_tel, to_tel, sender, text): 
    if text == 'connector':
        """Change this"""
        # po_box = connections[from_tel][to_tel]['po_box_uuid']
        # return f'Use connector {po_box[0:4]} to make postcard connection to viewers.'    

    if 'connect' in text and text != 'connector':
        """ --> Call connects.disconnect_viewer and  connects.connect_requester_to_granted_pobox"""
        # return connect_command(sender, to_tel)

    if 'from:' in text:
        try:    
            cmd, name = [word.strip() for word in text.split(' ')]
            assert cmd == 'from:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        sender['conn'][to_tel]['from'] = name
        return f'You will now be identified to others in your sending group by {name} rather than by your sending telephone number.'

    if 'to:' in text and len(text.split(' '))==2:
        try:    
            cmd, new_name = [word.strip() for word in text.split(' ')]
            assert cmd == 'to:'
        except (ValueError, AssertionError):
            if os.environ['TEST'] == 'True':
                raise
            return f'Sorry, there is some problem with, "{text}". Try "?" for help.'
        former_name = sender['conn'][to_tel]['to']
        sender['conn'][to_tel]['to'] = new_name
        return f'Renamed recipient {former_name} to {new_name}'

    else:
        return f"Do not recognize commmand '{text}'. Send '?' for more help."



