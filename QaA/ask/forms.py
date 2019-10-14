from django import forms
from .fields import *


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = UsernameField(max_length=20, required=True)
    password = PasswordField(min_length=6, required=True,
                             error_messages={"min_length": "Password to short. Must be at least 6 characters long"})
    password_repeat = forms.CharField(min_length=6, required=True)
    email = EmailField(required=True)

    def clean_password(self):
        try:
            password = self.cleaned_data['password']

            validator = SimilarityValidator(max_similarity=0.5)
            validator.validate(
                password, user=self.cleaned_data)
        except ValidationError:
            raise forms.ValidationError(
                'The password is too similar to the username')
        except KeyError:
            return None
        return password

    def clean_password_repeat(self):
        try:
            password = self.cleaned_data['password']
            password_repeat = self.cleaned_data['password_repeat']
        except KeyError:
            return None

        if password != password_repeat:
            raise forms.ValidationError('Password does not match')
        return password_repeat
