from django import forms


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(min_length=6, required=True,
                               error_messages={"min_length": "Password to short. Must be at least 6 characters long"})
    email = forms.EmailField(required=True)
