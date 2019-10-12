from django import forms


class SignUpForm(forms.Form):
    username = forms.CharField(label="username", max_length=20)
