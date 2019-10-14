from django import forms
from django.contrib.auth.models import User


class UsernameField(forms.CharField):

    def validate(self, value):
        super().validate(value)
        queryset = User.objects.filter(username=value)
        if len(queryset) != 0:
            raise forms.ValidationError("Username already taken")


class EmailField(forms.EmailField):

    def validate(self, value):
        super().validate(value)
        queryset = User.objects.filter(email=value)
        if len(queryset) != 0:
            raise forms.ValidationError("Email address already taken")


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = UsernameField(max_length=20, required=True)
    password = forms.CharField(min_length=6, required=True,
                               error_messages={"min_length": "Password to short. Must be at least 6 characters long"})
    password_repeat = forms.CharField(min_length=6, required=True)
    email = EmailField(required=True)

    def clean_password_repeat(self):
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']

        if password != password_repeat:
            raise forms.ValidationError('Password does not match')
        return password_repeat
