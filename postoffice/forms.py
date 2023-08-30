from django import forms

class ConnectionsForm(forms.Form):
    tel_id = forms.CharField(label="First, enter the phone number you are sending from. Enter as: ' +1<10digits> ' ", max_length=40)
    passkey = forms.CharField(label="Second, enter the 4-character 'connector'. See instructions, hotlink above. ",max_length=40)
