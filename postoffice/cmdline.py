img1 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MM948cc579dc1dddcad6ff4545f7f68473/Media/ME18c2f52a4a3be36b2fb3609598187a13"
audio1 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE71fa37807272ce5bb2e13a7716dccbaf.mp3"
img2 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MMa8fc1b190596c0adf840f5d042ff442c/Media/ME0c9e8b0191dc098d8c60aca5a86b3a4c"
audio2 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE4b40cfb563d4890c1776b24f2a96099b.mp3"
img3 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Messages/MM1bbb4ad2a748f5c91145730bb1814bb6/Media/ME2a2ad0d70f188d079fb7bfebd28e0af0"
audio3 = "https://api.twilio.com/2010-04-01/Accounts/AC976ed9a0260acd7d8c05fd6a013bcecf/Recordings/RE57fb3bc1c0b5776098ac78d450b1dd40.mp3"

from django.http.response import HttpResponse

from filer import views as filerviews 

from postmaster import test_cmds


def make_playable_viewer_data():
    filerviews.clear_the_read_bucket()
    filerviews.clear_the_sqs_queue_TEST_SQS()
    viewer_data = test_cmds.make_two_sender_viewer_data()
    for from_tel in viewer_data:
        viewer_data[from_tel]['profile_url'] = img2    
        viewer_data[from_tel]['image_url'] = img1      
        viewer_data[from_tel]['audio_url'] = audio1     
    return viewer_data


def played_this_card(request, card_id):
    print(f'\npostoffice cmdline got played_this_card for card_id:\n{card_id}\n')
    return HttpResponse()






import cmd

class CarePostRunner(cmd.Cmd):
    intro = 'Welcome to the twilio simulator.'
    prompt = 'sqs cmd:'
    file = None
    def do_new_sender(self, *args):
        print('this is an empty command!')
    def do_exit(self, *args):
        return True

if __name__ == "__main__":
    interpreter = CarePostRunner()
    interpreter.cmdloop()







