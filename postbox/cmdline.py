

from django.http.response import HttpResponse


from postoffice import test_cmds


def played_this_card(request, card_id):
    print(f'\npostoffice cmdline got played_this_card for card_id:\n{card_id}\n')
    return HttpResponse()


