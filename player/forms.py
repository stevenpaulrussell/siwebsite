from django import forms

class ConnectionsForm(forms.Form):
    from_tel = forms.CharField(label="First, enter the phone number you are sending from. Enter as: ' +1<10digits> ' ", max_length=40)
    connector = forms.CharField(label="Second, enter the 4-character 'connector'. See instructions, hotlink above. ",max_length=40)
